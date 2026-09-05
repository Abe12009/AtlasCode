import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as fs from 'fs';

const en = JSON.parse(fs.readFileSync('./src/locales/en.json', 'utf-8'));

async function test() {
  const instance = i18n.createInstance();
  
  await instance
    .use(initReactI18next)
    .init({
      resources: {
        en: { translation: en },
      },
      fallbackLng: 'en',
      lng: 'en',
      debug: true,
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
      keySeparator: '.',
      nsSeparator: ':',
    });
  
  console.log('i18n initialized');
  console.log('t(common.preferred_language):', instance.t('common.preferred_language'));
  console.log('t(auth.create_account_text):', instance.t('auth.create_account_text'));
  console.log('isInitialized:', instance.isInitialized);
  
  // Check the resource store directly
  const store = instance.services.resourceStore.data;
  console.log('Resource store en.translation.common:', JSON.stringify(store.en?.translation?.common, null, 2));
}

test().catch(console.error);