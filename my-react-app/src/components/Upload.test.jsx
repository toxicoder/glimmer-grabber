import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import Upload from './Upload';
import api from '../utils/api';

jest.mock('../utils/api');

describe('Upload', () => {
  it('renders the upload form', () => {
    render(
      <MemoryRouter>
        <Upload />
      </MemoryRouter>
    );
    expect(screen.getByLabelText('Select a file')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
  });

  it('allows the user to select a file', () => {
    render(
      <MemoryRouter>
        <Upload />
      </MemoryRouter>
    );
    const fileInput = screen.getByLabelText('Select a file');
    const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(fileInput.files[0]).toBe(file);
    expect(fileInput.files.length).toBe(1);
  });

  it('displays an error message when the upload fails', async () => {
    api.post.mockRejectedValue({
      response: {
        data: {
          detail: 'Invalid image format',
        },
      },
    });

    render(
      <MemoryRouter>
        <Upload />
      </MemoryRouter>
    );

    const fileInput = screen.getByLabelText('Select a file');
    const file = new File(['(⌐□_□)'], 'chucknorris.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    const uploadButton = screen.getByRole('button', { name: 'Upload' });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid image format')).toBeInTheDocument();
    });
  });
});
