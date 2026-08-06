/* ============================================
   DSC — Digital Services Center
   Main JavaScript
   ============================================ */

(function () {
  'use strict';

  /* --- Navbar scroll effect --- */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --- Mobile menu toggle --- */
  const toggle = document.querySelector('.navbar__toggle');
  const navLinks = document.querySelector('.navbar__links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const spans = toggle.querySelectorAll('span');
      if (navLinks.classList.contains('open')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        const spans = toggle.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '';
        spans[2].style.transform = '';
      });
    });
  }

  /* --- Scroll animations --- */
  const animElements = document.querySelectorAll('.animate-on-scroll');
  if (animElements.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );
    animElements.forEach(el => observer.observe(el));
  }

  /* --- Active nav link --- */
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.navbar__links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });

  /* --- Service filter (services.html) --- */
  const filterBtns = document.querySelectorAll('.filter-btn');
  const serviceCards = document.querySelectorAll('.service-card[data-category]');
  if (filterBtns.length && serviceCards.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.dataset.filter;
        serviceCards.forEach(card => {
          if (cat === 'all' || card.dataset.category === cat) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  /* --- Order form logic (order.html) --- */
  const orderForm = document.getElementById('orderForm');
  if (orderForm) {
    const serviceSelect = document.getElementById('serviceSelect');
    const quantityInput = document.getElementById('quantity');
    const priceDisplay = document.getElementById('priceEstimate');
    const summaryService = document.getElementById('summaryService');
    const summaryQty = document.getElementById('summaryQty');
    const summaryTotal = document.getElementById('summaryTotal');

    const prices = {
      'feasibility-study': { min: 8000, max: 25000, label: 'Étude de faisabilité' },
      'business-plan': { min: 5000, max: 15000, label: 'Business Plan' },
      'market-study': { min: 6000, max: 18000, label: 'Étude de marché' },
      'g12': { min: 3000, max: 5000, label: 'Déclaration G12' },
      'g50': { min: 5000, max: 10000, label: 'Déclaration G50' },
      'g4': { min: 2000, max: 4000, label: 'Déclaration G4' },
      'g11': { min: 3000, max: 6000, label: 'Déclaration G11' },
      'g29': { min: 4000, max: 8000, label: 'Déclaration G29' },
      'g1': { min: 2500, max: 5000, label: 'Déclaration G1' },
      'g8': { min: 2000, max: 4000, label: 'Déclaration G8' },
      'rnc': { min: 2000, max: 4000, label: 'Immatriculation RNC' },
      'nis': { min: 1500, max: 3000, label: 'Numéro NIS' },
      'nif': { min: 1500, max: 3000, label: 'Numéro NIF' },
      'rc': { min: 3000, max: 6000, label: 'Registre de Commerce' },
      'attestation': { min: 1000, max: 2500, label: 'Attestation fiscale' },
      'logo-design': { min: 5000, max: 15000, label: 'Design de logo' },
      'business-card': { min: 2000, max: 5000, label: 'Carte de visite' },
      'flyer': { min: 3000, max: 8000, label: 'Flyer / Dépliant' },
      'letterhead': { min: 2000, max: 5000, label: 'Papier en-tête' },
      'other': { min: 2000, max: 10000, label: 'Autre service' }
    };

    function updatePrice() {
      const service = serviceSelect.value;
      const qty = parseInt(quantityInput.value) || 1;
      const p = prices[service];

      if (p) {
        const totalMin = p.min * qty;
        const totalMax = p.max * qty;
        priceDisplay.textContent = formatDZD(totalMin) + ' – ' + formatDZD(totalMax);
        if (summaryService) summaryService.textContent = p.label;
        if (summaryQty) summaryQty.textContent = qty + ' × ' + formatDZD(p.min) + ' – ' + formatDZD(p.max);
        if (summaryTotal) summaryTotal.textContent = formatDZD(totalMin) + ' – ' + formatDZD(totalMax);
      }
    }

    function formatDZD(n) {
      return new Intl.NumberFormat('fr-DZ').format(n) + ' DZD';
    }

    serviceSelect.addEventListener('change', updatePrice);
    quantityInput.addEventListener('input', updatePrice);
    updatePrice();

    /* Pre-select service from URL */
    const params = new URLSearchParams(location.search);
    const preselect = params.get('service');
    if (preselect && serviceSelect.querySelector('option[value="' + preselect + '"]')) {
      serviceSelect.value = preselect;
      updatePrice();
    }

    /* Form validation + WhatsApp send */
    orderForm.addEventListener('submit', function (e) {
      e.preventDefault();
      let valid = true;

      const fields = ['clientName', 'clientEmail', 'clientPhone', 'serviceSelect'];
      fields.forEach(id => {
        const field = document.getElementById(id);
        const group = field.closest('.form-group');
        if (!field.value.trim()) {
          group.classList.add('error');
          valid = false;
        } else {
          group.classList.remove('error');
        }
      });

      if (!valid) return;

      const service = serviceSelect.value;
      const p = prices[service];
      const qty = parseInt(quantityInput.value) || 1;
      const details = document.getElementById('clientDetails').value;

      let msg = 'Bonjour DSC,\n\n';
      msg += 'Je souhaite commander un service :\n\n';
      msg += '📋 Service : ' + (p ? p.label : service) + '\n';
      msg += '📊 Quantité : ' + qty + '\n';
      msg += '💰 Budget estimé : ' + priceDisplay.textContent + '\n\n';
      msg += '👤 Nom : ' + document.getElementById('clientName').value + '\n';
      msg += '📧 Email : ' + document.getElementById('clientEmail').value + '\n';
      msg += '📱 Téléphone : ' + document.getElementById('clientPhone').value + '\n';
      if (details) {
        msg += '\n📝 Détails :\n' + details + '\n';
      }
      msg += '\nMerci !';

      const encoded = encodeURIComponent(msg);
      window.open('https://wa.me/213676773892?text=' + encoded, '_blank');
    });
  }

  /* --- Contact form (contact.html) --- */
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      let valid = true;

      ['contactName', 'contactEmail', 'contactMessage'].forEach(id => {
        const field = document.getElementById(id);
        const group = field.closest('.form-group');
        if (!field.value.trim()) {
          group.classList.add('error');
          valid = false;
        } else {
          group.classList.remove('error');
        }
      });

      if (!valid) return;

      const name = document.getElementById('contactName').value;
      const email = document.getElementById('contactEmail').value;
      const phone = document.getElementById('contactPhone').value;
      const message = document.getElementById('contactMessage').value;

      let msg = 'Bonjour DSC,\n\n';
      msg += 'Nouveau message de contact :\n\n';
      msg += '👤 Nom : ' + name + '\n';
      msg += '📧 Email : ' + email + '\n';
      if (phone) msg += '📱 Téléphone : ' + phone + '\n';
      msg += '\n💬 Message :\n' + message;

      const encoded = encodeURIComponent(msg);
      window.open('https://wa.me/213676773892?text=' + encoded, '_blank');

      contactForm.style.display = 'none';
      document.getElementById('contactSuccess').classList.add('show');
    });
  }

})();
