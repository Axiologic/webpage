(() => {
  const formClass = 'ml-subscribe-form-45068192';
  const endpoint = 'https://assets.mailerlite.com/jsonp/2588619/forms/196410360596530306/subscribe';
  const submitFrameName = 'newsletter-submission-frame';
  const mounts = [...document.querySelectorAll('[data-newsletter-form]')];
  const formMarkup = (emailId) => `<form class="ml-block-form" action="${endpoint}" data-code="" method="post" target="${submitFrameName}"><label class="sr-only" for="${emailId}">Email</label><input id="${emailId}" aria-label="email" aria-required="true" type="email" name="fields[email]" placeholder="Email" autocomplete="email" required><input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true"><button type="submit">Subscribe</button></form>`;
  if (!document.querySelector(`iframe[name="${submitFrameName}"]`)) {
    const submitFrame = document.createElement('iframe');
    submitFrame.name = submitFrameName;
    submitFrame.title = 'Newsletter submission';
    submitFrame.hidden = true;
    document.body.append(submitFrame);
  }
  if (!document.querySelector('link[href*="assets/css/site.css"]')) {
    const fallbackStyles = document.createElement('style');
    fallbackStyles.textContent = '.newsletter-header-actions{display:flex;align-items:center;justify-content:flex-end;gap:18px;margin-left:auto}.newsletter-top-trigger{position:static;padding:10px 16px;border:1px solid #9af2c6;border-radius:999px;background:#11151d;color:#9af2c6;cursor:pointer;font:600 14px Arial,sans-serif}.main-nav .newsletter-top-trigger{margin-left:18px}.newsletter-page-controls{display:flex;justify-content:flex-end;padding:16px}.newsletter-modal{position:fixed;z-index:100;inset:0;display:grid;place-items:center;padding:20px;background:rgba(4,7,12,.72)}.newsletter-dialog{position:relative;width:min(100%,860px);padding:42px;border-radius:16px;background:#11151d;color:#fff;font-family:Arial,sans-serif}.newsletter-dialog h2{margin:8px 42px 12px 0;font-size:30px;line-height:1.12;white-space:nowrap}.newsletter-dialog p{margin:0 0 28px;color:#cbd1dc;font-size:18px;line-height:1.55;white-space:nowrap}.newsletter-dialog input,.newsletter-dialog button{box-sizing:border-box;width:100%;min-height:46px;margin-top:10px;padding:11px 13px;border-radius:8px;font:inherit}.newsletter-dialog button{border:0;background:#9af2c6;color:#0a1514;font-weight:700}.newsletter-close{position:absolute;top:14px;right:14px;border:0;background:transparent;color:#fff;font-size:24px;cursor:pointer}@media(max-width:900px){.newsletter-dialog h2,.newsletter-dialog p{white-space:normal}}';
    document.head.append(fallbackStyles);
  }

  const showSuccess = () => {
    document.querySelectorAll(`.${formClass}`).forEach((form) => {
      form.innerHTML = '<p class="newsletter-success">Thank you! You have successfully joined our subscriber list.</p>';
    });
  };
  window.ml_webform_success_45068192 = showSuccess;
  let mailerLiteLoaded = false;
  const loadMailerLite = () => {
    if (mailerLiteLoaded) return;
    mailerLiteLoaded = true;
    const script = document.createElement('script');
    script.src = 'https://groot.mailerlite.com/js/w/webforms.min.js?v83147fa8ce2d95cb73ece7f28b469519';
    script.async = true;
    document.head.append(script);
    fetch('https://assets.mailerlite.com/jsonp/2588619/forms/196410360596530306/takel').catch(() => {});
  };

  mounts.forEach((mount) => {
    mount.id = 'mlb2-45068192';
    mount.classList.add('newsletter-form', 'ml-form-embedContainer', 'ml-subscribe-form', formClass);
    mount.innerHTML = formMarkup('newsletter-email');
  });
  if (mounts.length) loadMailerLite();

  const closeModal = () => document.querySelector('.newsletter-modal')?.remove();
  const openNewsletter = () => {
    closeModal();
    loadMailerLite();
    const modal = document.createElement('div');
    modal.className = 'newsletter-modal';
    modal.innerHTML = `<div class="newsletter-dialog" role="dialog" aria-modal="true" aria-labelledby="newsletter-modal-title"><button class="newsletter-close" type="button" aria-label="Close newsletter signup">×</button><span class="eyebrow">Newsletter</span><h2 id="newsletter-modal-title">Get notified when new editions are released.</h2><p>Occasional updates about new books and revisions.</p><div class="newsletter-form ${formClass}">${formMarkup('newsletter-popup-email')}</div></div>`;
    modal.addEventListener('click', (event) => { if (event.target === modal) closeModal(); });
    modal.querySelector('.newsletter-close').addEventListener('click', closeModal);
    modal.querySelector('form').addEventListener('submit', () => {
      window.setTimeout(() => {
        modal.querySelector(`.${formClass}`)?.replaceChildren(Object.assign(document.createElement('p'), {
          className: 'newsletter-success', textContent: 'Thank you! You have successfully joined our subscriber list.'
        }));
      }, 200);
    });
    document.body.append(modal);
    modal.querySelector('input').focus();
  };
  document.querySelectorAll('.edition-actions').forEach((actions) => {
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'btn ghost newsletter-trigger';
    trigger.textContent = 'Subscribe';
    trigger.addEventListener('click', openNewsletter);
    actions.append(trigger);
  });
  const topTrigger = document.createElement('button');
  topTrigger.type = 'button';
  topTrigger.className = 'newsletter-top-trigger';
  topTrigger.textContent = 'Subscribe';
  topTrigger.addEventListener('click', openNewsletter);
  const pageHeader = document.querySelector('.books-header, .top-bar');
  if (pageHeader) {
    const headerActions = document.createElement('div');
    headerActions.className = 'newsletter-header-actions';
    pageHeader.querySelectorAll(':scope > .back-link').forEach((link) => headerActions.append(link));
    headerActions.append(topTrigger);
    pageHeader.append(headerActions);
  } else {
    const legacyNavigation = document.querySelector('.main-nav');
    if (legacyNavigation) {
      legacyNavigation.append(topTrigger);
    } else {
      const pageControls = document.createElement('div');
      pageControls.className = 'newsletter-page-controls';
      pageControls.append(topTrigger);
      document.body.prepend(pageControls);
    }
  }
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeModal(); });
})();
