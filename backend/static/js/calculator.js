function funeralCalculator() {
    return {
        // Состояние
        loading: true,
        submitting: false,
        submitSuccess: false,
        leadId: null,
        currentTab: 'new',
        allCategories: [],

        // Цена за платное вскрытие
        AUTOPSY_PAID_PRICE: 3000,

        // Выбранные услуги для каждой вкладки
        selectedServices: {
            new: [],
            relative: [],
            cremation: []
        },

        // Данные формы
        formData: {
            name: '',
            phone: '',
            comment: '',
            autopsyType: 'paid'
        },

        // Ошибки
        errors: {
            name: '',
            phone: '',
            services: ''
        },

        // Инициализация
        async initCalculator() {
            try {
                const apiUrl = '/api/catalog/';
                const response = await fetch(apiUrl);
                const data = await response.json();
                this.allCategories = data;

                // НЕ выбираем ничего автоматически
            } catch (error) {
                console.error('Ошибка загрузки каталога:', error);
                alert('Не удалось загрузить каталог услуг. Попробуйте обновить страницу.');
            } finally {
                this.loading = false;
            }
        },

        // Переключение вкладки
        switchTab(tab) {
            this.currentTab = tab;
            this.errors.services = '';
        },

        // Проверка применимости услуги к вкладке
        serviceAppliesToTab(service, tab) {
            if (service.applicability === 'all') return true;
            if (service.applicability === 'funeral' && (tab === 'new' || tab === 'relative')) return true;
            if (service.applicability === 'cremation' && tab === 'cremation') return true;
            return false;
        },

        // Отфильтрованные категории для текущей вкладки
        get filteredCategories() {
            return this.allCategories
                .map(category => ({
                    ...category,
                    services: category.services.filter(service =>
                        this.serviceAppliesToTab(service, this.currentTab)
                    )
                }))
                .filter(category => category.services.length > 0);
        },

        // Проверка выбранной услуги
        isSelected(serviceId) {
            return this.selectedServices[this.currentTab].includes(serviceId);
        },

        // Переключение услуги
        toggleService(serviceId, selectionType) {
            const currentSelected = this.selectedServices[this.currentTab];
            const index = currentSelected.indexOf(serviceId);

            if (selectionType === 'single') {
                // Для radio: находим категорию этой услуги
                const category = this.allCategories.find(cat =>
                    cat.services.some(s => s.id === serviceId)
                );

                if (category) {
                    // Сначала удаляем ВСЕ услуги этой категории из выбора
                    category.services.forEach(s => {
                        const idx = currentSelected.indexOf(s.id);
                        if (idx > -1) {
                            currentSelected.splice(idx, 1);
                        }
                    });

                    // Если кликнули на уже выбранный элемент - просто снимаем выбор (не добавляем обратно)
                    // Если кликнули на новый - добавляем его
                    if (index === -1) {
                        currentSelected.push(serviceId);
                    }
                    // Если index !== -1, значит мы сняли выбор и не добавляем ничего (отмена выбора)
                }
            } else {
                // Для checkbox: обычное добавление/удаление
                if (index > -1) {
                    currentSelected.splice(index, 1);
                } else {
                    currentSelected.push(serviceId);
                }
            }
        },

        // Расчёт общей суммы
        calculateTotal() {
            let total = 0;
            const currentSelected = this.selectedServices[this.currentTab];

            // Считаем выбранные услуги
            this.allCategories.forEach(category => {
                category.services.forEach(service => {
                    if (currentSelected.includes(service.id)) {
                        total += parseFloat(service.price);
                    }
                });
            });

            // Добавляем стоимость вскрытия если выбрано платное
            if (this.formData.autopsyType === 'paid') {
                total += this.AUTOPSY_PAID_PRICE;
            }

            return total;
        },

        // Получение стоимости вскрытия для отображения
        getAutopsyPrice() {
            if (this.formData.autopsyType === 'paid') {
                return this.AUTOPSY_PAID_PRICE;
            }
            return 0;
        },

        // Форматирование цены
        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB',
                minimumFractionDigits: 0
            }).format(price);
        },

        // Валидация телефона
        validatePhone() {
            const phone = this.formData.phone.replace(/\D/g, '');

            if (phone.length === 0) {
                this.errors.phone = '';
                return;
            }

            if (phone.length < 11) {
                this.errors.phone = 'Введите полный номер телефона';
                return false;
            }

            if (phone.length > 11) {
                this.errors.phone = 'Слишком много цифр';
                return false;
            }

            if (!['7', '8'].includes(phone[0])) {
                this.errors.phone = 'Номер должен начинаться с +7 или 8';
                return false;
            }

            this.errors.phone = '';
            return true;
        },

        // Проверка минимального набора услуг
        validateMinimumServices() {
            const currentSelected = this.selectedServices[this.currentTab];

            if (currentSelected.length === 0) {
                this.errors.services = 'Выберите хотя бы одну услугу';
                return false;
            }

            // Для захоронений: обязательно должен быть гроб (категория 1)
            if (this.currentTab === 'new' || this.currentTab === 'relative') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));

                if (!hasCoffin) {
                    this.errors.services = 'Для захоронения обязательно выберите гроб';
                    return false;
                }
            }

            // Для кремации: обязательно гроб + кремация
            if (this.currentTab === 'cremation') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));

                const hasCremation = this.allCategories
                    .find(cat => cat.id === 8)?.services
                    .some(s => currentSelected.includes(s.id));

                if (!hasCoffin) {
                    this.errors.services = 'Для кремации обязательно выберите гроб';
                    return false;
                }

                if (!hasCremation) {
                    this.errors.services = 'Для кремации обязательно выберите услугу кремации';
                    return false;
                }
            }

            this.errors.services = '';
            return true;
        },

        // Проверка доступности кнопки отправки
        get canSubmit() {
            const currentSelected = this.selectedServices[this.currentTab];

            if (currentSelected.length === 0) return false;

            if (this.currentTab === 'new' || this.currentTab === 'relative') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));
                if (!hasCoffin) return false;
            }

            if (this.currentTab === 'cremation') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));
                const hasCremation = this.allCategories
                    .find(cat => cat.id === 8)?.services
                    .some(s => currentSelected.includes(s.id));
                if (!hasCoffin || !hasCremation) return false;
            }

            if (!this.formData.name.trim()) return false;
            if (!this.validatePhone()) return false;

            return true;
        },

        // Подсказка почему кнопка неактивна
        getSubmitHint() {
            const currentSelected = this.selectedServices[this.currentTab];

            if (currentSelected.length === 0) {
                return '⚠️ Выберите хотя бы одну услугу';
            }

            if (this.currentTab === 'new' || this.currentTab === 'relative') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));
                if (!hasCoffin) {
                    return '⚠️ Для захоронения обязательно выберите гроб';
                }
            }

            if (this.currentTab === 'cremation') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));
                const hasCremation = this.allCategories
                    .find(cat => cat.id === 8)?.services
                    .some(s => currentSelected.includes(s.id));
                if (!hasCoffin) {
                    return '⚠️ Для кремации обязательно выберите гроб';
                }
                if (!hasCremation) {
                    return '⚠️ Для кремации обязательно выберите услугу кремации';
                }
            }

            if (!this.formData.name.trim()) {
                return '⚠️ Введите ваше имя';
            }

            if (!this.validatePhone()) {
                return '⚠️ Введите корректный номер телефона';
            }

            return '';
        },

        // Отправка заявки
        async submitLead() {
            this.errors.name = '';
            this.errors.phone = '';
            this.errors.services = '';

            if (!this.formData.name.trim()) {
                this.errors.name = 'Введите ваше имя';
                return;
            }

            if (!this.validatePhone()) {
                return;
            }

            if (!this.validateMinimumServices()) {
                return;
            }

            this.submitting = true;

            const leadData = {
                client_name: this.formData.name.trim(),
                phone: this.formData.phone.replace(/\D/g, ''),
                funeral_type: this.currentTab,
                autopsy_type: this.formData.autopsyType,
                selected_services: [...this.selectedServices[this.currentTab]],
                estimated_total: this.calculateTotal(),
                comment: this.formData.comment.trim()
            };

            try {
                const response = await fetch('/api/orders/lead/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify(leadData)
                });

                const result = await response.json();

                if (result.status === 'success') {
                    this.submitSuccess = true;
                    this.leadId = result.lead_id;
                } else {
                    alert('Ошибка отправки: ' + result.message);
                }
            } catch (error) {
                console.error('Ошибка отправки заявки:', error);
                alert('Не удалось отправить заявку. Попробуйте позже.');
            } finally {
                this.submitting = false;
            }
        },

        // Получение CSRF токена
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        // Сброс формы
        resetForm() {
            this.submitSuccess = false;
            this.leadId = null;
            this.formData.name = '';
            this.formData.phone = '';
            this.formData.comment = '';
            this.formData.autopsyType = 'paid';
            this.selectedServices = {
                new: [],
                relative: [],
                cremation: []
            };
            this.currentTab = 'new';
            this.errors.services = '';
        }
    }
}

// Маска для телефона
document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('client_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', (e) => {
            const value = e.target.value;
            const digits = value.replace(/\D/g, '').slice(0, 11);

            if (digits.length === 0) {
                e.target.value = '';
                return;
            }

            let formatted = '+7';
            if (digits[0] === '8') {
                digits[0] = '7';
            }

            if (digits.length > 1) formatted += ' (' + digits.slice(1, 4);
            if (digits.length > 4) formatted += ') ' + digits.slice(4, 7);
            if (digits.length > 7) formatted += '-' + digits.slice(7, 9);
            if (digits.length > 9) formatted += '-' + digits.slice(9, 11);

            e.target.value = formatted;
        });
    }
});
