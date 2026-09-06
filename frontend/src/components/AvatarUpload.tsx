import { useRef, useState } from 'react';
import { Upload } from 'lucide-react';
import { Button, Alert } from './ui';
import { useTranslation } from '../hooks/useTranslation';

const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/webp'];
const MAX_UPLOAD_BYTES = 8 * 1024 * 1024; // before compression, generous
const TARGET_DIMENSION = 256; // square output
const MAX_ENCODED_BYTES = 480_000; // server caps at 500KB

/** Reads a File, center-crops it to a square, and downscales it so the
 * resulting data URL is comfortably under the server's size cap. This is a
 * basic automatic crop rather than an interactive one — good enough for a
 * profile picture without pulling in a cropping library. */
async function processImageFile(file: File): Promise<string> {
  const objectUrl = URL.createObjectURL(file);
  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Could not read image'));
      img.src = objectUrl;
    });

    const side = Math.min(image.width, image.height);
    const sx = (image.width - side) / 2;
    const sy = (image.height - side) / 2;

    const canvas = document.createElement('canvas');
    canvas.width = TARGET_DIMENSION;
    canvas.height = TARGET_DIMENSION;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Canvas not supported');
    ctx.drawImage(image, sx, sy, side, side, 0, 0, TARGET_DIMENSION, TARGET_DIMENSION);

    // Step down JPEG quality until the encoded size fits the cap.
    let quality = 0.9;
    let dataUrl = canvas.toDataURL('image/jpeg', quality);
    while (dataUrl.length > MAX_ENCODED_BYTES && quality > 0.3) {
      quality -= 0.15;
      dataUrl = canvas.toDataURL('image/jpeg', quality);
    }
    return dataUrl;
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

export function AvatarUpload({
  onUpload,
  uploading,
}: {
  onUpload: (dataUrl: string) => void;
  uploading?: boolean;
}) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState('');

  const handleFile = async (file: File | undefined) => {
    setError('');
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError(t('avatar.upload_error_type'));
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setError(t('avatar.upload_error_size'));
      return;
    }

    try {
      const dataUrl = await processImageFile(file);
      onUpload(dataUrl);
    } catch {
      setError(t('avatar.upload_error_generic'));
    }
  };

  return (
    <div className="space-y-3">
      {error && <Alert variant="error">{error}</Alert>}
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <Button
        type="button"
        variant="outline"
        leftIcon={<Upload className="h-4 w-4" />}
        loading={uploading}
        onClick={() => inputRef.current?.click()}
      >
        {t('avatar.upload_photo')}
      </Button>
      <p className="text-xs text-text-tertiary">{t('avatar.upload_hint')}</p>
    </div>
  );
}
