# backend/chat/services.py
import os
import requests
import openai
import logging
import numpy as np
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from django.db import connection
import PyPDF2
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from django.conf import settings


OPENAI_KEY = settings.OPENAI_KEY
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
LLM_MODEL = settings.LLM_MODEL
MAX_DOCUMENTS = settings.MAX_DOCUMENTS


# Configure enhanced logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for creating embeddings for documents"""
    
    def __init__(self):
        self.api_key = OPENAI_KEY
        self.embedding_model = EMBEDDING_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Check your .env file.")
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text using OpenAI's API
        
        Args:
            text: The text to create an embedding for
            
        Returns:
            A list of floats representing the embedding vector
        """
        logger.debug(f"Creating embedding for text of length {len(text)} characters")
        
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "input": text,
            "model": self.embedding_model
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            logger.debug(f"Successfully created embedding of dimension {len(embedding)}")
            
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
    
    def process_document(self, document):
        """
        Create and store an embedding for a document
        
        Args:
            document: The Document model instance
            
        Returns:
            The updated Document with embedding
        """
        logger.info(f"Processing document: {document.id} - {document.title}")
        
        embedding = self.create_embedding(document.content)
        document.embedding = embedding
        document.save()
        
        logger.info(f"Document processed successfully: {document.id}")
        
        return document


class VectorSearchService:
    """Service for performing vector similarity search"""
    
    def __init__(self, embedding_service=None):
        from .models import Document
        self.Document = Document
        self.embedding_service = embedding_service or EmbeddingService()
    
    def search_similar_documents(self, query: str, top_k: int = 3, user=None) -> List[Tuple[Any, float]]:
        """
        Find documents similar to the query using vector similarity
        
        Args:
            query: The query text
            top_k: Number of documents to return
            user: User to filter documents by (optional)
            
        Returns:
            List of tuples containing (document, similarity_score)
        """
        logger.info(f"Searching for documents similar to query: '{query}'")
        logger.info(f"User filter: {user.username if user else 'None'}")
        start_time = time.time()
        
        # Generate embedding for the query
        query_embedding = np.array(self.embedding_service.create_embedding(query))
        logger.debug(f"Generated query embedding with shape: {query_embedding.shape}")
        
        # Get only active documents with embeddings
        documents_query = self.Document.objects.filter(
            embedding__isnull=False,
            is_active=True  # Only use active documents
        )
        
        # If user is provided, filter documents by user
        if user:
            documents_query = documents_query.filter(user=user)
            
        documents = documents_query.all()
        
        logger.info(f"Found {len(documents)} active documents with embeddings")
        
        # Calculate similarity scores
        document_scores = []
        for doc in documents:
            doc_embedding = np.array(doc.embedding)
            
            # Calculate cosine similarity
            logger.debug(f"Calculating similarity for document: {doc.id} - {doc.title}")
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            document_scores.append((doc, similarity))
            logger.debug(f"Document {doc.id} ({doc.title[:30]}{'...' if len(doc.title) > 30 else ''}) - Score: {similarity:.4f}")
        
        # Sort by similarity (highest first) and take top_k
        document_scores.sort(key=lambda x: x[1], reverse=True)
        top_docs = document_scores[:top_k]
        
        logger.info(f"Top {len(top_docs)} document matches:")
        for i, (doc, score) in enumerate(top_docs):
            logger.info(f"  {i+1}. Score: {score:.4f} - Document: {doc.id} - {doc.title}")
            logger.debug(f"     Content preview: {doc.content[:100]}...")
        
        logger.info(f"Document search completed in {time.time() - start_time:.2f} seconds")
        return top_docs
    
    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors with logging"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        similarity = dot_product / (norm_a * norm_b)
        logger.debug(f"Similarity score: {similarity:.4f}")
        return similarity


class LLMService:
    """Service for interacting with the LLM using the OpenAI v1+ API"""
    
    def __init__(self):
        from openai import OpenAI
        
        # Use the API key from config
        self.api_key = OPENAI_KEY
        self.model = LLM_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Check your .env file.")
        
        # Initialize the client with the API key
        self.client = OpenAI(api_key=self.api_key)
        
        # Default fallback prompt if no prompt is found in database
        self.default_prompt = {
            "assistant_role": "You are a helpful AI assistant that provides information based on the context provided.",
            "response_guidelines": "Be concise, accurate, and helpful. If you don't know the answer based on the provided context, say so.",
            "restrictions": "Only answer based on the context provided. Do not make up information."
        }
    
    def get_active_prompt(self, user=None):
        """
        Get the active prompt from the database
        
        Args:
            user: The user to get the prompt for (optional)
            
        Returns:
            Active Prompt model instance or None
        """
        from .models import Prompt
        
        try:
            prompt_query = Prompt.objects.filter(is_active=True)
            
            # Filter by user if provided
            if user:
                prompt_query = prompt_query.filter(user=user)
                
            active_prompt = prompt_query.first()
            
            if active_prompt:
                logger.info(f"Using active prompt from database: {active_prompt.name} (User: {user.username if user else 'None'})")
                return active_prompt
            
            logger.info("No active prompt found in database, will use default")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching active prompt: {str(e)}")
            logger.info("Using default prompt values due to error")
            return None
    
    def generate_response(self, query: str, context: str, history: List[Dict[str, str]] = None, user=None) -> str:
        """
        Generate a response from the LLM with detailed logging of all prompts
        
        Args:
            query: The user's question
            context: Context information retrieved from documents
            history: Optional conversation history
            user: The user making the request (optional)
            
        Returns:
            The LLM's response
        """
        if history is None:
            history = []
        
        # Get the active prompt for the specific user or use defaults
        active_prompt = self.get_active_prompt(user=user)
        
        # Generate the system prompt
        if active_prompt:
            # Use the prompt's generate_system_prompt method
            system_prompt = active_prompt.generate_system_prompt(dynamic_context=context)
        else:
            # Create a basic default prompt
            sections = []
            sections.append(f"# Role\n{self.default_prompt['assistant_role']}")
            sections.append(f"# Retrieved Information\n{context}")
            sections.append(f"# Response Guidelines\n{self.default_prompt['response_guidelines']}")
            sections.append(f"# Limitations\n{self.default_prompt['restrictions']}")
            system_prompt = "\n\n".join(sections)
        
        # Log the full prompt context
        logger.info("=============== FULL CONTEXT WINDOW ===============")
        logger.info(f"Context documents (length: {len(context)} chars):\n{context}")
        logger.info("=============== END CONTEXT ===============")
        
        # Prepare the messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        if history:
            logger.info("=============== CONVERSATION HISTORY ===============")
            for msg in history:
                logger.info(f"{msg['role'].upper()}: {msg['content']}")
                messages.append({"role": msg["role"], "content": msg["content"]})
            logger.info("=============== END HISTORY ===============")
        
        # Add the current query
        logger.info(f"CURRENT QUERY: {query}")
        messages.append({"role": "user", "content": query})
        
        # Log the full message structure being sent to OpenAI
        logger.debug("=============== FULL OPENAI MESSAGES ===============")
        for msg in messages:
            logger.debug(f"ROLE: {msg['role']}")
            logger.debug(f"CONTENT: {msg['content']}")
            logger.debug("---")
        logger.debug("=============== END OPENAI MESSAGES ===============")
        
        try:
            start_time = time.time()
            logger.info("Sending request to OpenAI API...")
            
            # Call the OpenAI API using the new client format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            logger.info(f"OpenAI API response received in {time.time() - start_time:.2f} seconds")
            response_text = response.choices[0].message.content
            
            # Log the model's response
            logger.info("=============== MODEL RESPONSE ===============")
            logger.info(response_text)
            logger.info("=============== END RESPONSE ===============")
            
            return response_text
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"


class RAGService:
    """Service implementing the RAG pipeline"""
    
    def __init__(self):
        from .models import Conversation, Message
        self.Conversation = Conversation
        self.Message = Message
        self.vector_search = VectorSearchService()
        self.llm_service = LLMService()
    
    def process_query(self, query: str, conversation_id: Optional[str] = None, user=None) -> Tuple[str, List[Any]]:
        """
        Process a user query with detailed logging of the entire RAG pipeline
        
        Args:
            query: The user's question
            conversation_id: Optional ID of an existing conversation
            user: The user making the query (optional)
            
        Returns:
            Tuple containing (response, relevant_documents)
        """
        logger.info("=============== NEW QUERY PROCESSING ===============")
        logger.info(f"Query: '{query}'")
        logger.info(f"Conversation ID: {conversation_id}")
        logger.info(f"User: {user.username if user else 'Anonymous'}")
        start_time = time.time()
        
        # 1. Retrieve similar documents
        logger.info("STEP 1: Retrieving similar documents...")
        document_scores = self.vector_search.search_similar_documents(query, top_k=3, user=user)
        relevant_documents = [doc for doc, _ in document_scores]
        
        # 2. Format documents as context
        logger.info("STEP 2: Formatting documents as context...")
        context = "\n\n".join([
            f"Document {i+1} ({doc.title}):\n{doc.content}" 
            for i, doc in enumerate(relevant_documents)
        ])
        
        # 3. Get conversation history if conversation_id is provided
        logger.info("STEP 3: Retrieving conversation history...")
        history = []
        conversation = None
        
        if conversation_id:
            try:
                # If user is provided, ensure the conversation belongs to the user
                conversation_query = self.Conversation.objects.filter(session_id=conversation_id)
                if user:
                    conversation_query = conversation_query.filter(user=user)
                    
                conversation = conversation_query.first()
                
                if conversation:
                    logger.info(f"Found existing conversation: {conversation.session_id}")
                    messages = self.Message.objects.filter(conversation=conversation).order_by('timestamp')
                    
                    # Take the last 5 messages to keep context manageable
                    for msg in messages.order_by('-timestamp')[:5]:
                        history.append({
                            "role": msg.role,
                            "content": msg.content
                        })
                    history.reverse()  # Put in chronological order
                    
                    logger.info(f"Retrieved {len(history)} message(s) from history")
                else:
                    logger.info("No existing conversation found or it doesn't belong to the user")
                
            except self.Conversation.DoesNotExist:
                logger.info("No existing conversation found, will create a new one")
                # If conversation doesn't exist, we'll create a new one
                pass
        
        # 4. Generate response using the LLM
        logger.info("STEP 4: Generating response using LLM...")
        response = self.llm_service.generate_response(query, context, history, user=user)
        
        # 5. Save conversation and messages to database
        logger.info("STEP 5: Saving conversation and messages...")
        if not conversation:
            # Create new conversation if none exists
            conversation_id = f"conv_{self.Conversation.objects.count() + 1}"
            
            # Add user if provided
            conversation_data = {'session_id': conversation_id}
            if user:
                conversation_data['user'] = user
                
            conversation = self.Conversation.objects.create(**conversation_data)
            logger.info(f"Created new conversation with ID: {conversation_id}")
        
        # Save user message
        user_message = self.Message.objects.create(
            conversation=conversation,
            role='user',
            content=query
        )
        logger.debug(f"Saved user message with ID: {user_message.id}")
        
        # Save assistant response
        assistant_message = self.Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response
        )
        logger.debug(f"Saved assistant message with ID: {assistant_message.id}")
        
        # Link relevant documents to the assistant's message
        for doc in relevant_documents:
            assistant_message.reference_documents.add(doc)
        logger.debug(f"Linked {len(relevant_documents)} reference document(s) to response")
        
        logger.info(f"Query processing completed in {time.time() - start_time:.2f} seconds")
        logger.info("=============== END QUERY PROCESSING ===============")
        
        return response, relevant_documents


class DocumentProcessingService:
    """Service for processing different document types"""
    
    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service or EmbeddingService()
    
    def process_pdf(self, pdf_file, title=None, chunk_size=10000, chunk_overlap=200, user=None):
        """
        Process a PDF file by extracting text, splitting into chunks, and storing with embeddings
        
        Args:
            pdf_file: The PDF file object (BytesIO or file path)
            title: Optional title for the document
            chunk_size: Size of text chunks to split into
            chunk_overlap: Overlap between chunks to maintain context
            user: The user who uploaded the document (optional)
            
        Returns:
            List of created Document objects
        """
        from .models import Document
        
        logger.info(f"Processing PDF file: {title if title else 'Unnamed PDF'}")
        logger.info(f"User: {user.username if user else 'None'}")
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(pdf_file)
        
        if not text.strip():
            logger.error("No text could be extracted from the PDF")
            raise ValueError("No text could be extracted from the PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Split text into chunks
        chunks = self._split_text(text, chunk_size, chunk_overlap)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # Generate title if not provided
        if not title:
            title = f"PDF Document ({len(chunks)} chunks)"
        
        # Create documents and embeddings for each chunk
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_title = f"{title} - Part {i+1}"
            logger.debug(f"Processing chunk {i+1}/{len(chunks)}: {chunk_title}")
            
            # Add user if provided
            doc_data = {
                'title': chunk_title,
                'content': chunk,
                'source': title,
            }
            
            if user:
                doc_data['user'] = user
                
            doc = Document.objects.create(**doc_data)
            
            # Generate embedding
            self.embedding_service.process_document(doc)
            documents.append(doc)
        
        logger.info(f"PDF processing completed: {len(documents)} documents created")
        return documents
    
    def _extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file"""
        if isinstance(pdf_file, str):  # If it's a filepath
            logger.debug(f"Extracting text from PDF file path: {pdf_file}")
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.debug(f"Extracted page {i+1}/{len(pdf_reader.pages)}: {len(page_text)} characters")
        else:  # If it's a file object or BytesIO
            logger.debug("Extracting text from uploaded PDF file")
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                logger.debug(f"Extracted page {i+1}/{len(pdf_reader.pages)}: {len(page_text)} characters")
        
        return text
    
    def _split_text(self, text, chunk_size=1000, chunk_overlap=200):
        """Split text into overlapping chunks"""
        logger.debug(f"Splitting text with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        logger.debug(f"Text split into {len(chunks)} chunks")
        
        return chunks

# New service classes for Phase 2 organization

class BackgroundService:
    """Service for managing background images"""
    
    @staticmethod
    def get_active_background(user):
        """Get the active background for a user"""
        from .models import BackgroundImage
        return BackgroundImage.objects.filter(is_active=True, user=user).first()
    
    @staticmethod
    def list_backgrounds(user):
        """List all backgrounds for a user"""
        from .models import BackgroundImage
        return BackgroundImage.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def create_background(name, image_file, is_active, user):
        """Create a new background image"""
        from .models import BackgroundImage
        return BackgroundImage.objects.create(
            name=name,
            image=image_file,
            is_active=is_active,
            user=user
        )
    
    @staticmethod
    def set_active_background(background_id, user):
        """Set a background as active for a user"""
        from .models import BackgroundImage
        background = BackgroundImage.objects.get(id=background_id, user=user)
        background.is_active = True
        background.save()
        return background
    
    @staticmethod
    def delete_background(background_id, user):
        """Delete a background image"""
        from .models import BackgroundImage
        background = BackgroundImage.objects.get(id=background_id, user=user)
        
        # Delete the image file
        if background.image and os.path.isfile(background.image.path):
            os.remove(background.image.path)
        
        # Delete the database record
        background.delete()
        return True

class DocumentService:
    """Service for managing documents"""
    
    @staticmethod
    def list_documents(user):
        """List all documents for a user"""
        from .models import Document
        return Document.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def get_active_documents(user):
        """Get active documents for a user"""
        from .models import Document
        return Document.objects.filter(is_active=True, user=user).order_by('-created_at')
    
    @staticmethod
    def set_active_documents(document_ids, user):
        """Set specified documents as active for a user"""
        from .models import Document
        
        # Deactivate all documents for this user first
        Document.objects.filter(user=user).update(is_active=False)
        
        # Then activate only the selected ones, ensuring they belong to the user
        updated = Document.objects.filter(
            id__in=document_ids,
            user=user
        ).update(is_active=True)
        
        return updated
    
    @staticmethod
    def delete_document(document_id, user):
        """Delete a document and all related documents with the same source"""
        from .models import Document
        
        # Get the document and ensure it belongs to the current user
        document = Document.objects.get(id=document_id, user=user)
        source = document.source
        
        # Delete all documents with the same source that belong to this user
        deleted_count = Document.objects.filter(source=source, user=user).delete()[0]
        return deleted_count

class PromptService:
    """Service for managing prompt templates"""
    
    @staticmethod
    def get_prompt(user):
        """Get user's prompt, creating default if none exists"""
        from .models import Prompt
        
        prompt = Prompt.objects.filter(user=user).first()
        
        if not prompt:
            # Create default prompt for this user if none exists
            prompt = Prompt.objects.create(
                user=user,
                name="Default Assistant",
                assistant_role="You are a helpful AI assistant answering questions based on the provided context.",
                website_context="",
                knowledge_context="",
                response_guidelines="Provide concise, accurate answers based on the context provided. Use bullet points for lists. If you don't know the answer, say so.",
                restrictions="Only answer based on the provided context. Do not make up information.",
                is_active=True
            )
        
        return prompt
    
    @staticmethod
    def update_prompt(prompt_data, user):
        """Update user's prompt"""
        from .models import Prompt
        
        prompt = Prompt.objects.filter(user=user).first()
        
        if not prompt:
            # Create a new prompt if none exists
            prompt = Prompt()
            prompt.user = user
        
        # Update fields if provided
        if 'name' in prompt_data:
            prompt.name = prompt_data['name']
        if 'assistant_role' in prompt_data:
            prompt.assistant_role = prompt_data['assistant_role']
        if 'website_context' in prompt_data:
            prompt.website_context = prompt_data['website_context']
        if 'knowledge_context' in prompt_data:
            prompt.knowledge_context = prompt_data['knowledge_context']
        if 'response_guidelines' in prompt_data:
            prompt.response_guidelines = prompt_data['response_guidelines']
        if 'restrictions' in prompt_data:
            prompt.restrictions = prompt_data['restrictions']
        
        prompt.is_active = True
        prompt.save()
        return prompt

class SettingsService:
    """Service for managing chat settings"""
    
    @staticmethod
    def get_settings(user):
        """Get active settings for a user, creating default settings if none exist"""
        from .models import Settings
        
        settings = Settings.objects.filter(is_active=True, user=user).first()
        
        if not settings:
            # Create default settings for this user if none exist
            settings = Settings.objects.create(
                user=user,
                chatName='Diákszámla Zéró AI Asszisztens',
                colorPrimary='#4B5563',
                buttonBg='#4B5563',
                welcomeMessage="A PanelGPT AI Asszisztens segít gyors és megbízható válaszokat kapni a panelfelújítással kapcsolatos kérdéseidre.",
                disclaimerTitle='Üdvözöljük a Diákszámla Zéró Asszisztensnél',
                disclaimerIntro='Mielőtt elkezdenénk a beszélgetést, kérjük, vegye figyelembe az alábbiakat:',
                disclaimerPoints=[
                    'Az AI Asszisztens csak általános információkat szolgáltat a Diákszámla Zéró csomagról.',
                    'Ne adjon meg személyes adatokat, bankszámlaszámot vagy jelszavakat ebben a chatben.',
                    'Az AI nem látja és nem tárolja az Ön személyes bank adatait.'
                ],
                acceptButtonText="Elfogadom és folytatom",
                sendButtonText="Küldés",
                footerDisclaimer="Ez az AI asszisztens a nyilvánosan elérhető adatok alapján ad információt.",
                privacyPolicyText="Adatvédelmi tájékoztató",
                is_active=True
            )
        
        return settings
    
    @staticmethod
    def update_settings(settings_data, user):
        """Update settings for a user"""
        from .models import Settings
        
        # Get active settings for the current user or create new
        settings = Settings.objects.filter(is_active=True, user=user).first()
        if not settings:
            settings = Settings()
            settings.is_active = True
            settings.user = user
        
        # Update fields if provided
        field_map = {
            'chatName': 'chatName',
            'colorPrimary': 'colorPrimary',
            'buttonBg': 'buttonBg',
            'welcomeMessage': 'welcomeMessage',
            'disclaimerTitle': 'disclaimerTitle',
            'disclaimerIntro': 'disclaimerIntro',
            'disclaimerPoints': 'disclaimerPoints',
            'acceptButtonText': 'acceptButtonText',
            'sendButtonText': 'sendButtonText',
            'footerDisclaimer': 'footerDisclaimer',
            'privacyPolicyText': 'privacyPolicyText'
        }
        
        for api_field, model_field in field_map.items():
            if api_field in settings_data:
                setattr(settings, model_field, settings_data[api_field])
        
        settings.save()
        return settings