// Shared analytics configuration for every public page.
(() => {
  if (document.getElementById('site-umami')) return;

  const script = document.createElement('script');
  script.id = 'site-umami';
  script.defer = true;
  script.src = 'https://bizanso.com/base-agent-additional-server/umamiAgent/3000/script.js';
  script.dataset.websiteId = 'a5aae3b0-ba4a-4d7a-b3ad-4f1428053ec3';
  document.head.appendChild(script);
})();
