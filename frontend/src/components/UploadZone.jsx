/**
 * UploadZone — drag-and-drop PDF uploader with progress indicator.
 */
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../services/api';

const MAX_MB = 50;

export default function UploadZone({ onUploaded }) {
  const [state, setState] = useState('idle'); // idle | uploading | success | error
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [fileName, setFileName] = useState('');

  const ACCEPTED_EXTS = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.webp', '.bmp'];

  const handleUpload = useCallback(async (files) => {
    const file = files[0];
    if (!file) return;

    // Client-side validation
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ACCEPTED_EXTS.includes(ext)) {
      setState('error');
      setMessage('Unsupported file type. Please upload a PDF, PNG, JPG, JPEG, TIFF, WEBP, or BMP file.');
      return;
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setState('error');
      setMessage(`File exceeds the ${MAX_MB} MB size limit.`);
      return;
    }

    setFileName(file.name);
    setState('uploading');
    setProgress(0);

    const form = new FormData();
    form.append('file', file);

    try {
      const { data } = await uploadDocument(form, (evt) => {
        if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100));
      });

      if (data.document.status === 'error') {
        setState('error');
        setMessage(data.document.error_message || data.message);
      } else {
        setState('success');
        setMessage(data.message);
        onUploaded && onUploaded(data.document);
      }
    } catch (err) {
      setState('error');
      setMessage(
        err.response?.data?.detail ||
        'Upload failed. Make sure the backend is running.'
      );
    }
  }, [onUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleUpload,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff', '.tif'],
      'image/webp': ['.webp'],
      'image/bmp': ['.bmp'],
    },
    multiple: false,
  });

  const reset = () => { setState('idle'); setMessage(''); setFileName(''); setProgress(0); };

  return (
    <div>
      {(state === 'idle' || state === 'error') && (
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} id="pdf-upload-input" />
          <div className="dropzone-icon">
            <Upload size={26} />
          </div>
          <div className="dropzone-title">
            {isDragActive ? 'Drop your file here…' : 'Drag & drop a legal document'}
          </div>
          <div className="dropzone-sub">PDF · PNG · JPG · TIFF · WEBP · BMP &nbsp;·&nbsp; max {MAX_MB} MB &nbsp;·&nbsp; images auto-converted via OCR</div>
          {state === 'error' && (
            <div className="alert alert-error" style={{ marginTop: 16, textAlign: 'left' }}>
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              {message}
            </div>
          )}
        </div>
      )}

      {state === 'uploading' && (
        <div style={{ textAlign: 'center', padding: '32px 24px' }}>
          <Loader2 size={36} className="animate-spin-slow" style={{ color: 'var(--navy-600)', margin: '0 auto 16px' }} />
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Processing "{fileName}"…</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
            {fileName.match(/\.(png|jpe?g|tiff?|webp|bmp)$/i)
              ? 'Converting image to PDF, running OCR, and building vector index…'
              : 'Extracting text (with automatic OCR for scanned pages) and building vector index…'}
          </div>
          <div className="progress-bar" style={{ maxWidth: 320, margin: '0 auto' }}>
            <div className="progress-fill" style={{ width: `${Math.max(progress, 8)}%`, transition: 'width .3s' }} />
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>{progress}% uploaded</div>
        </div>
      )}

      {state === 'success' && (
        <div style={{ textAlign: 'center', padding: '32px 24px' }}>
          <CheckCircle2 size={40} style={{ color: 'var(--success)', margin: '0 auto 14px', display: 'block' }} />
          <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Upload successful!</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>{message}</div>
          <button className="btn btn-secondary" onClick={reset}>Upload another document</button>
        </div>
      )}
    </div>
  );
}
