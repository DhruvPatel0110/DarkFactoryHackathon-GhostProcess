/**
 * GhostProcess Modal Dialog System
 */

export const modal = {
  open(title, bodyHtml, footerButtons = []) {
    const backdrop = document.getElementById('modal-backdrop');
    const container = document.getElementById('modal-container');
    if (!backdrop || !container) return;

    let footerHtml = '';
    if (footerButtons.length > 0) {
      footerHtml = `
        <div class="modal-footer">
          ${footerButtons.map(btn => `
            <button class="${btn.class || 'btn btn-secondary'}" id="${btn.id || ''}">
              ${btn.text}
            </button>
          `).join('')}
        </div>
      `;
    }

    container.innerHTML = `
      <div class="modal-header">
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close" id="modal-close-x" aria-label="Close Modal">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        ${bodyHtml}
      </div>
      ${footerHtml}
    `;

    backdrop.classList.add('open');

    const close = () => {
      backdrop.classList.remove('open');
    };

    const closeBtn = document.getElementById('modal-close-x');
    if (closeBtn) closeBtn.onclick = close;

    backdrop.onclick = (e) => {
      if (e.target === backdrop) close();
    };

    // Attach footer button handlers
    footerButtons.forEach(btn => {
      if (btn.id && btn.onClick) {
        const el = document.getElementById(btn.id);
        if (el) {
          el.onclick = (e) => btn.onClick(e, close);
        }
      }
    });

    return { close };
  },

  close() {
    const backdrop = document.getElementById('modal-backdrop');
    if (backdrop) backdrop.classList.remove('open');
  }
};
