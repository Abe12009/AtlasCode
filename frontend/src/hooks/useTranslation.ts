import { useTranslation as useTranslationOrg } from 'react-i18next';

export function useTranslation(namespace?: string) {
  const { t, i18n } = useTranslationOrg(namespace);
  
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('i18nextLng', lng);
  };
  
  // i18n.language can be a full locale like "en-US" or "fr-CA" when detected from the
  // browser (navigator.language). The backend only accepts the bare "en"/"fr"/"ar" codes,
  // so normalize here — the single place every API call and RTL check reads from.
  const currentLanguage = (i18n.language || 'en').split('-')[0];
  const isRTL = currentLanguage === 'ar';
  
  return {
    t,
    i18n,
    changeLanguage,
    currentLanguage,
    isRTL,
    languages: [
      { code: 'en', name: 'English', nativeName: 'English' },
      { code: 'fr', name: 'French', nativeName: 'Français' },
      { code: 'ar', name: 'Arabic', nativeName: 'العربية' }
    ]
  };
}