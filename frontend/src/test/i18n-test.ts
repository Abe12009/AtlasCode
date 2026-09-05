import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import en from '../locales/en.json';
import fr from '../locales/fr.json';
import ar from '../locales/ar.json';

export async function createTestI18n() {
  const instance = i18n.createInstance();
  
  await instance
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
        fr: { translation: fr },
        ar: { translation: ar },
      },
      fallbackLng: 'en',
      lng: 'en',
      debug: false,
      interpolation: {
        escapeValue: false,
      },
      detection: {
        order: [],
        caches: [],
      },
      react: {
        useSuspense: false,
      },
      ignoreJSONStructure: false,
    });
  
  return instance;
}