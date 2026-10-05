(() => {
  const form = document.querySelector('#contact-form');
  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;

    const fields = new FormData(form);
    const recipient = [108, 101, 97, 100, 115, 64, 97, 120, 105, 111, 108, 111, 103, 105, 99, 46, 110, 101, 116]
      .map((code) => String.fromCharCode(code))
      .join('');
    const organization = String(fields.get('organization') || '').trim();
    const bodyLines = [
      `Name: ${String(fields.get('name') || '').trim()}`,
      `Work email: ${String(fields.get('email') || '').trim()}`,
    ];
    if (organization) bodyLines.push(`Organization: ${organization}`);
    bodyLines.push('', 'Project or problem:', String(fields.get('project') || '').trim());
    const body = bodyLines.join('\n');
    const subject = organization
      ? `Project enquiry from ${organization}`
      : 'Project enquiry for Axiologic Research';

    window.location.href = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
})();
