/* SmartHealth AI - Client Scripting & Dynamic Symptom Filter */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Dynamic Symptom Search Filter
    const symptomSearchInput = document.getElementById('symptomSearchInput');
    if (symptomSearchInput) {
        symptomSearchInput.addEventListener('keyup', function () {
            const query = this.value.toLowerCase().trim();
            const symptomItems = document.querySelectorAll('.symptom-item-col');

            symptomItems.forEach(item => {
                const name = item.getAttribute('data-symptom-name').toLowerCase();
                const code = item.getAttribute('data-symptom-code').toLowerCase();
                const category = item.getAttribute('data-symptom-category').toLowerCase();

                if (name.includes(query) || code.includes(query) || category.includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // 2. Symptom Card Selection State Toggle
    const symptomCards = document.querySelectorAll('.symptom-card');
    symptomCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        const detailControls = card.querySelector('.symptom-details-controls');

        if (checkbox) {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    card.classList.add('selected');
                    if (detailControls) detailControls.classList.remove('d-none');
                } else {
                    card.classList.remove('selected');
                    if (detailControls) detailControls.classList.add('d-none');
                }
                updateSelectedCount();
            });
        }
    });

    function updateSelectedCount() {
        const selectedCheckboxes = document.querySelectorAll('.symptom-checkbox:checked');
        const badge = document.getElementById('selectedSymptomCountBadge');
        if (badge) {
            badge.textContent = selectedCheckboxes.length;
        }
    }

    // 3. Category Filter Buttons
    const categoryBtns = document.querySelectorAll('.category-filter-btn');
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            categoryBtns.forEach(b => b.classList.remove('active', 'btn-primary'));
            categoryBtns.forEach(b => b.classList.add('btn-outline-secondary'));

            this.classList.remove('btn-outline-secondary');
            this.classList.add('active', 'btn-primary');

            const selectedCat = this.getAttribute('data-category');
            const symptomItems = document.querySelectorAll('.symptom-item-col');

            symptomItems.forEach(item => {
                const itemCat = item.getAttribute('data-symptom-category');
                if (selectedCat === 'all' || itemCat === selectedCat) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // 4. Quick Preset Symptom Bundles
    const presetBtns = document.querySelectorAll('.preset-btn');
    presetBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const symCodes = this.getAttribute('data-symptoms').split(',');
            symCodes.forEach(code => {
                const cb = document.getElementById('sym_' + code.trim());
                if (cb) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change'));
                }
            });
        });
    });

    const clearAllBtn = document.getElementById('clearAllSymptomsBtn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function () {
            const checkboxes = document.querySelectorAll('.symptom-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = false;
                cb.dispatchEvent(new Event('change'));
            });
        });
    }

    // 5. Auto dismiss flash alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });
});

