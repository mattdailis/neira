/**
 * Page Layout Web Component
 * Provides consistent header and container layout for all pages
 * Port from neira_ui_svelte/src/routes/+layout.svelte
 *
 * Uses Shadow DOM for true encapsulation and native <slot> support
 */

class PageLayout extends HTMLElement {
  connectedCallback() {
    // Create shadow root for encapsulation
    const shadow = this.attachShadow({ mode: 'open' });

    shadow.innerHTML = `
      <!-- Load component stylesheet -->
      <link rel="stylesheet" href="css/page-layout.css">

      <!-- Top navigation bar -->
      <div class="top-bar">
        <span>neira</span>
      </div>

      <!-- Main page content area -->
      <div class="main-content">
        <slot></slot>
      </div>
    `;
  }
}

// Register the custom element
customElements.define('page-layout', PageLayout);
