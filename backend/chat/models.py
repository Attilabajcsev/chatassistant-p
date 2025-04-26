# backend/chat/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class Document(models.Model):
    """Store documents and their vector embeddings for retrieval"""

    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    embedding = ArrayField(
        models.FloatField(), 
        null=True, 
        blank=True,
        help_text="Vector embedding of the document content"
    )
    source = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='documents',
        null=True
    )
    
    def __str__(self):
        return self.title or f"Document {self.id}"

class Conversation(models.Model):
    """Track chat conversations"""
    session_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='conversations',
        null=True
    )

    def __str__(self):
        return f"Conversation {self.session_id}"

class Message(models.Model):
    """Store individual chat messages"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    reference_documents = models.ManyToManyField(
        Document, 
        related_name='referenced_in',
        blank=True
    )

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class BackgroundImage(models.Model):
    """Store background images for different use cases"""
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='backgrounds/')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='backgrounds',
        null=True
    )

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):

        if self.is_active and self.user:
            BackgroundImage.objects.filter(
                is_active=True, 
                user=self.user
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

class Prompt(models.Model):
    """Store flexible prompt templates for the AI assistant"""
    name = models.CharField(max_length=255)
    
    # Core sections of the prompt
    assistant_role = models.TextField(
        help_text="Defines who the assistant is and its general purpose",
        default="You are a helpful AI assistant answering questions about a website's content."
    )
    
    website_context = models.TextField(
        help_text="General information about the website/company the assistant represents",
        blank=True
    )
    
    knowledge_context = models.TextField(
        help_text="Fixed knowledge the assistant should always have access to",
        blank=True
    )
    
    response_guidelines = models.TextField(
        help_text="Guidelines for how the assistant should format and structure responses",
        default="Provide concise, accurate information based on the context provided."
    )
    
    # For special instructions and restrictions
    restrictions = models.TextField(
        help_text="Constraints or limitations on what the assistant should or shouldn't do",
        blank=True
    )
    
    # Fields for managing prompts
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='prompts',
        null=True
    )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.is_active = True
        super().save(*args, **kwargs)
    
    def generate_system_prompt(self, dynamic_context=""):
        """
        Generate the full system prompt by combining all sections
        
        Args:
            dynamic_context: The RAG-retrieved context to include
        
        Returns:
            The complete system prompt text
        """
        sections = []
        
        # Add role definition
        sections.append(f"# Role\n{self.assistant_role}")
        
        # Add website context if available
        if self.website_context:
            sections.append(f"# Website Information\n{self.website_context}")
        
        # Add knowledge context if available
        if self.knowledge_context:
            sections.append(f"# Background Knowledge\n{self.knowledge_context}")
        
        # Add dynamic context from RAG if available
        if dynamic_context:
            sections.append(f"# Retrieved Information\n{dynamic_context}")
        
        # Add response guidelines
        sections.append(f"# Response Guidelines\n{self.response_guidelines}")
        
        # Add restrictions if available
        if self.restrictions:
            sections.append(f"# Limitations and Restrictions\n{self.restrictions}")
        
        # Combine all sections with double newlines for clarity
        return "\n\n".join(sections)

class Settings(models.Model):
    """Store chat settings and appearance configuration"""
    chatName = models.CharField(max_length=255, default='Chat Assistant')
    colorPrimary = models.CharField(max_length=50, default='#4B5563')
    buttonBg = models.CharField(max_length=50, default='#4B5563')
    welcomeMessage = models.TextField(default="Welcome! How can I help you today?")
    disclaimerTitle = models.CharField(max_length=255, default='Welcome to the Chat Assistant')
    disclaimerIntro = models.TextField(default='Please review the following information before we start:')
    disclaimerPoints = models.JSONField(default=list)  # Store as JSON array
    acceptButtonText = models.CharField(max_length=100, default='Accept and Continue')
    sendButtonText = models.CharField(max_length=100, default='Send')
    footerDisclaimer = models.TextField(default='This AI assistant provides information based on publicly available data.')
    privacyPolicyText = models.CharField(max_length=100, default='Privacy Policy')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='settings',
        null=True
    )
    
    def __str__(self):
        return f"Settings: {self.chatName}"
    
    def save(self, *args, **kwargs):

        if self.is_active and self.user:
            Settings.objects.filter(
                is_active=True,
                user=self.user
            ).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_defaults(sender, instance, created, **kwargs):
    """
    Default values for the user
    """
    if created:

        Settings.objects.create(
            user=instance,
            chatName='Chat Assistant',
            colorPrimary='#4B5563',
            buttonBg='#4B5563',
            welcomeMessage="Welcome! How can I help you today?",
            disclaimerTitle='Welcome to the Chat Assistant',
            disclaimerIntro='Please review the following information before we start:',
            disclaimerPoints=[
                'This AI assistant provides general information only.',
                'Do not share sensitive personal information in this chat.',
                'The AI cannot see or store your personal data.'
            ],
            acceptButtonText="Accept and Continue",
            sendButtonText="Send",
            footerDisclaimer="This AI assistant provides information based on publicly available data.",
            privacyPolicyText="Privacy Policy",
            is_active=True
        )
        

        Prompt.objects.create(
            user=instance,
            name="Default Assistant",
            assistant_role="You are a helpful AI assistant answering questions based on the provided context.",
            website_context="",
            knowledge_context="",
            response_guidelines="Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
            restrictions="Only answer based on the provided context. Do not make up information.",
            is_active=True
        )

        logger.info(f"Created default settings and prompt for new user: {instance.username}")