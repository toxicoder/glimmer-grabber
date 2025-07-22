import unittest
import hashlib
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from processing_service.tasks import process_image_task
from shared.shared.models.models import ProcessingJob, ProcessedImage, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        # Set up an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        # Clean up the database after each test
        Base.metadata.drop_all(self.engine)
        self.db.close()

    @patch('processing_service.tasks.extract_data')
    @patch('processing_service.tasks.process_image')
    @patch('processing_service.tasks.download_image_from_s3')
    @patch('processing_service.tasks.get_db')
    def test_process_new_image(self, mock_get_db, mock_download_image, mock_process_image, mock_extract_data):
        # Mocks
        def mock_get_db_gen():
            yield self.db
        mock_get_db.return_value = mock_get_db_gen()
        mock_download_image.return_value = b'fake_image_bytes'
        mock_process_image.return_value = ['card1']
        mock_extract_data.return_value = [{'name': 'Card A'}]

        # Create a fake job
        job = ProcessingJob(id=1, status='PENDING', s3_object_key='fake_key')
        self.db.add(job)
        self.db.commit()

        # Execute the task
        process_image_task(1, 'fake_key')

        # Assertions
        updated_job = self.db.query(ProcessingJob).filter(ProcessingJob.id == 1).first()
        self.assertEqual(updated_job.status, 'COMPLETED')

        processed_image = self.db.query(ProcessedImage).first()
        self.assertIsNotNone(processed_image)

    @patch('processing_service.tasks.download_image_from_s3')
    @patch('processing_service.tasks.get_db')
    def test_process_duplicate_image(self, mock_get_db, mock_download_image):
        # Mocks
        def mock_get_db_gen():
            yield self.db
        mock_get_db.return_value = mock_get_db_gen()
        image_bytes = b'fake_image_bytes_duplicate'
        mock_download_image.return_value = image_bytes
        image_hash = hashlib.sha256(image_bytes).hexdigest()

        # Pre-load the database with a processed image
        processed_image = ProcessedImage(hash=image_hash)
        self.db.add(processed_image)
        self.db.commit()

        # Create a fake job
        job = ProcessingJob(id=2, status='PENDING', s3_object_key='fake_key_dup')
        self.db.add(job)
        self.db.commit()

        # Execute the task
        process_image_task(2, 'fake_key_dup')

        # Assertions
        updated_job = self.db.query(ProcessingJob).filter(ProcessingJob.id == 2).first()
        self.assertEqual(updated_job.status, 'COMPLETED')
        # Verify that process_image and extract_data were not called
        # This requires more complex mocking of celery tasks or direct checks

if __name__ == '__main__':
    unittest.main()
