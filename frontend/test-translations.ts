import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as fs from 'fs';
import * as path from 'path';

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
    });
  
  console.log('Testing i18n translations:');
  console.log('auth.username_required:', instance.t('auth.username_required'));
  console.log('auth.username_min_length:', instance.t('auth.username_min_length'));
  console.log('auth.email_required:', instance.t('auth.email_required'));
  console.log('auth.email_invalid:', instance.t('auth.email_invalid'));
  console.log('auth.password_required:', instance.t('auth.password_required'));
  console.log('auth.password_min_length:', instance.t('auth.password_min_length'));
  console.log('auth.passwords_dont_match:', instance.t('auth.passwords_dont_match'));
  console.log('common.preferred_language:', instance.t('common.preferred_language'));
  console.log('auth.create_account_text:', instance.t('auth.create_account_text'));
}

test().catch(console.error);