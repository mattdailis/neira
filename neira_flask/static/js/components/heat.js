/**
 * Page Layout Web Component
 * Provides consistent header and container layout for all pages
 * Port from neira_ui_svelte/src/routes/+layout.svelte
 *
 * Uses Shadow DOM for true encapsulation and native <slot> support
 */

class Heat extends HTMLElement {
  connectedCallback() {
    // Create shadow root for encapsulation
    const shadow = this.attachShadow({ mode: 'open' });

    shadow.innerHTML = `
      <!-- Load component stylesheet -->
      <link rel="stylesheet" href="static/css/heat.css">

      <div class="race-results">
        <div class="race-header">
            <a class="row2k-link" target="_blank"><strong class="regatta-name"></strong></a>
            <span class="distance"></span>
        </div>
        <pre class="results-table"></pre>
      </div>

      <!-- Main page content area -->
      <div class="main-content">
        <slot></slot>
      </div>
    `;
  }
}

// Register the custom element
customElements.define('heat', Heat);
