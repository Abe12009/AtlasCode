import { useState } from 'react';
import { Check } from 'lucide-react';
import { AvatarFace } from './AvatarFace';
import { Button, cn } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import {
  ACCESSORIES,
  FACE_STYLES,
  HAIR_COLORS,
  HAIR_STYLES,
  OUTFITS,
  SKIN_TONES,
  type AvatarConfig,
} from '../lib/avatar';

function SwatchRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="mb-2 text-sm font-medium text-text-secondary">{label}</p>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  );
}

function ColorSwatch({ color, active, onClick, label }: { color: string; active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      className={cn(
        'h-9 w-9 rounded-full border-2 transition-transform duration-fast flex items-center justify-center',
        active ? 'border-primary-500 scale-110' : 'border-border-primary hover:scale-105',
      )}
      style={{ backgroundColor: color }}
    >
      {active && <Check className="h-4 w-4" style={{ color: '#fff', mixBlendMode: 'difference' }} />}
    </button>
  );
}

function LabelSwatch({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        'rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors duration-fast',
        active
          ? 'border-primary-500 bg-primary-500/10 text-primary-400'
          : 'border-border-primary text-text-secondary hover:border-border-secondary hover:text-text-primary',
      )}
    >
      {label}
    </button>
  );
}

export function AvatarBuilder({
  initialConfig,
  onSave,
  saving,
}: {
  initialConfig: AvatarConfig;
  onSave: (config: AvatarConfig) => void;
  saving?: boolean;
}) {
  const { t } = useTranslation();
  const [config, setConfig] = useState<AvatarConfig>(initialConfig);
  const update = <K extends keyof AvatarConfig>(key: K, value: AvatarConfig[K]) =>
    setConfig((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="grid gap-6 md:grid-cols-[200px_1fr]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-40 h-40 rounded-2xl bg-bg-secondary border border-border-primary overflow-hidden">
          <AvatarFace config={config} className="w-full h-full" />
        </div>
        <Button onClick={() => onSave(config)} loading={saving} fullWidth>
          {t('avatar.save')}
        </Button>
      </div>

      <div className="space-y-5">
        <SwatchRow label={t('avatar.skin_tone')}>
          {SKIN_TONES.map((tone) => (
            <ColorSwatch
              key={tone.id}
              color={tone.color}
              label={tone.label}
              active={config.skinTone === tone.id}
              onClick={() => update('skinTone', tone.id)}
            />
          ))}
        </SwatchRow>

        <SwatchRow label={t('avatar.hair_style')}>
          {HAIR_STYLES.map((style) => (
            <LabelSwatch
              key={style.id}
              label={style.label}
              active={config.hair === style.id}
              onClick={() => update('hair', style.id)}
            />
          ))}
        </SwatchRow>

        {config.hair !== 'bald' && (
          <SwatchRow label={t('avatar.hair_color')}>
            {HAIR_COLORS.map((color) => (
              <ColorSwatch
                key={color.id}
                color={color.color}
                label={color.id}
                active={config.hairColor === color.id}
                onClick={() => update('hairColor', color.id)}
              />
            ))}
          </SwatchRow>
        )}

        <SwatchRow label={t('avatar.face')}>
          {FACE_STYLES.map((style) => (
            <LabelSwatch
              key={style.id}
              label={style.label}
              active={config.face === style.id}
              onClick={() => update('face', style.id)}
            />
          ))}
        </SwatchRow>

        <SwatchRow label={t('avatar.outfit')}>
          {OUTFITS.map((outfit) => (
            <LabelSwatch
              key={outfit.id}
              label={outfit.label}
              active={config.outfit === outfit.id}
              onClick={() => update('outfit', outfit.id)}
            />
          ))}
        </SwatchRow>

        <SwatchRow label={t('avatar.accessory')}>
          {ACCESSORIES.map((accessory) => (
            <LabelSwatch
              key={accessory.id}
              label={accessory.label}
              active={config.accessory === accessory.id}
              onClick={() => update('accessory', accessory.id)}
            />
          ))}
        </SwatchRow>
      </div>
    </div>
  );
}
