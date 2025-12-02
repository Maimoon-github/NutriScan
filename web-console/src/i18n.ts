import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      upload: {
        title: 'Upload Nutrition Label',
        uploadButton: 'Upload Image',
        offlineBanner: 'You are offline. Use a sample image to demo.',
        sampleImages: 'Sample Images',
        stages: {
          uploading: 'Uploading',
          processing: 'Processing',
          analyzing: 'Analyzing'
        },
        retry: 'Retry Upload'
      },
      results: {
        title: 'Scan Results',
        summary: 'Summary',
        why: 'Why',
        ingredients: 'Ingredients',
        allergens: 'Allergens',
        swaps: 'Better Swaps'
      },
      errors: {
        validation: 'Validation error: please check your image and try again.',
        server: 'Server error: please retry.',
        network: 'Network error: please retry when online.'
      }
    }
  },
  ur: {
    translation: {
      upload: {
        title: 'غذائی لیبل اپ لوڈ کریں',
        uploadButton: 'تصویر اپ لوڈ کریں',
        offlineBanner: 'آپ آف لائن ہیں۔ ڈیمو کے لیے نمونہ تصویر استعمال کریں۔',
        sampleImages: 'نمونہ تصاویر',
        stages: {
          uploading: 'اپ لوڈ ہو رہا ہے',
          processing: 'پروسیسنگ',
          analyzing: 'تجزیہ'
        },
        retry: 'اپ لوڈ دوبارہ کریں'
      },
      results: {
        title: 'اسکین نتائج',
        summary: 'خلاصہ',
        why: 'کیوں',
        ingredients: 'اجزاء',
        allergens: 'ایلرجنز',
        swaps: 'بہتر متبادل'
      },
      errors: {
        validation: 'تصدیقی خرابی: براہ کرم تصویر چیک کریں۔',
        server: 'سرور خرابی: براہ کرم دوبارہ کوشش کریں۔',
        network: 'نیٹ ورک خرابی: آن لائن ہونے پر دوبارہ کوشش کریں۔'
      }
    }
  }
};

export function setupI18n() {
  const saved = localStorage.getItem('lang') || 'en';
  i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: saved,
      fallbackLng: 'en',
      interpolation: { escapeValue: false }
    });

  const root = document.documentElement;
  if (saved === 'ur') {
    root.setAttribute('dir', 'rtl');
  } else {
    root.setAttribute('dir', 'ltr');
  }

  return i18n;
}

export function setLanguage(lang: 'en' | 'ur') {
  localStorage.setItem('lang', lang);
  i18n.changeLanguage(lang);
  const root = document.documentElement;
  root.setAttribute('dir', lang === 'ur' ? 'rtl' : 'ltr');
}

export default i18n;
