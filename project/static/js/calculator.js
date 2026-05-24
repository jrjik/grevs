function funeralCalculator() {
    return {
        // Состояние
        loading: true,
        submitting: false,
        submitSuccess: false,
        leadId: null,
        currentTab: 'new',
        allCategories: [],

        // Цены за вскрытие
        AUTOPSY_QUEUE_PRICE: 8900,
        AUTOPSY_SAME_DAY_PRICE: 16550,

        // Выбранный пакет (null, 'basic', 'optimal', 'extended')
        selectedPackage: null,

        // Для отслеживания типа похорон при выборе пакета
        lastFuneralTypeForPackage: null,

        // Цены пакетов для захоронений (новая могила / подзахоронение)
        PACKAGE_PRICES_BURIAL: {
            basic: 35000,
            optimal: 58000,
            extended: 95000
        },

        // Цены пакетов для кремации
        PACKAGE_PRICES_CREMATION: {
            basic: 28000,
            optimal: 45000,
            extended: 75000
        },

        // Услуги пакетов для захоронений
        PACKAGE_SERVICES_BURIAL: {
            basic: [
                'Оформление документов',
                'Гроб шестигранный деревянный (обитый тканью)',
                'Крест эконом',
                'Табличка пластиковая',
                'Покрывало в гроб (тюль)',
                'Копка могилы',
                'Катафалк стандартный'
            ],
            optimal: [
                'Оформление документов',
                'Гроб шестигранный дерево-лак',
                'Крест металлический',
                'Табличка металлическая',
                'Покрывало в гроб (шелк)',
                'Копка могилы',
                'Катафалк стандартный',
                'Венок средний (1,20 м)',
                'Выносная группа (короткая, 1 точка)',
                'Отпевание',
                'Ограда на могилу'
            ],
            extended: [
                'Оформление документов',
                'Гроб дубовый',
                'Крест металлический',
                'Табличка металлическая',
                'Покрывало в гроб (стеганое)',
                'Копка могилы',
                'Катафалк иномарка',
                'Венок большой (1,5 м)',
                'Выносная группа (длинная, 2 точки)',
                'Отпевание',
                'Ограда на могилу',
                'Прощальный зал (батюшка + зал)',
                'Церковный набор (венчик, молитва, крест нательный, крест в руку, икона)'
            ]
        },

        // Услуги пакетов для кремации
        PACKAGE_SERVICES_CREMATION: {
            basic: [
                'Оформление документов',
                'Гроб шестигранный деревянный (обитый тканью) для кремации',
                'Урна пластиковая',
                'Табличка пластиковая',
                'Покрывало в гроб (тюль)',
                'Катафалк стандартный',
                'Кремация',
            ],
            optimal: [
                'Оформление документов',
                'Гроб шестигранный дерево-лак для кремации',
                'Урна металлическая',
                'Табличка металлическая',
                'Покрывало в гроб (шелк)',
                'Катафалк стандартный',
                'Кремация',
                'Венок средний (1,20 м)',
                'Отпевание',
            ],
            extended: [
                'Оформление документов',
                'Гроб четырехгранный двустворчатый лакированный для кремации',
                'Урна металлическая',
                'Табличка металлическая',
                'Покрывало в гроб (стеганое)',
                'Катафалк иномарка',
                'Кремация',
                'Венок большой (1,5 м)',
                'Отпевание',
                'Прощальный зал (батюшка + зал)',
                'Церковный набор (венчик, молитва, крест нательный, крест в руку, икона)'
            ]
        },

        selectedServices: {
            new: [],
            relative: [],
            cremation: []
        },

        formData: {
            name: '',
            phone: '',
            comment: '',
            autopsyType: 'queue',
            consent: false  
        },

        errors: {
            name: '',
            phone: '',
            services: '',
            consent: ''  
        },

        async initCalculator() {
            try {
                const apiUrl = '/api/catalog/';
                const response = await fetch(apiUrl);
                const data = await response.json();
                this.allCategories = data;

            } catch (error) {
                console.error('Ошибка загрузки каталога:', error);
                alert('Не удалось загрузить каталог услуг. Попробуйте обновить страницу.');
            } finally {
                this.loading = false;
            }
        },

        switchTab(tab) {
            if (this.selectedPackage && 
                ((tab === 'cremation') !== (this.currentTab === 'cremation'))) {
                this.selectedPackage = null;
                this.lastFuneralTypeForPackage = null;
            }
            
            this.currentTab = tab;
            this.errors.services = '';
        },

        serviceAppliesToTab(service, tab) {
            if (service.applicability === 'all') return true;
            if (service.applicability === 'funeral' && (tab === 'new' || tab === 'relative')) return true;
            if (service.applicability === 'cremation' && tab === 'cremation') return true;
            return false;
        },

        get filteredCategories() {
            const filtered = this.allCategories
                .map(category => ({
                    ...category,
                    services: category.services.filter(service =>
                        this.serviceAppliesToTab(service, this.currentTab)
                    )
                }))
                .filter(category => category.services.length > 0);
            
            if (this.currentTab === 'cremation') {
                return filtered.sort((a, b) => {
                    const priority = {
                        'Кремация': 1,
                        'Гробы': 2,
                        'Урны': 3,
                        'Колумбарий': 4
                    };
                    
                    const priorityA = priority[a.name] || 99;
                    const priorityB = priority[b.name] || 99;
                    
                    return priorityA - priorityB;
                });
            }
            
            return filtered;
        },

        isSelected(serviceId) {
            return this.selectedServices[this.currentTab].includes(serviceId);
        },

        toggleService(serviceId, selectionType) {
            const currentSelected = this.selectedServices[this.currentTab];
            const index = currentSelected.indexOf(serviceId);

            if (selectionType === 'single') {
                const category = this.allCategories.find(cat =>
                    cat.services.some(s => s.id === serviceId)
                );

                // снимаем все услуги категории, добавляем новую
                if (category) {
                    const isAlreadySelected = currentSelected.includes(serviceId);

                    category.services.forEach(s => {
                        const idx = currentSelected.indexOf(s.id);
                        if (idx > -1) {
                            currentSelected.splice(idx, 1);
                        }
                    });


                    if (!isAlreadySelected) {
                        currentSelected.push(serviceId);
                    }
                }
            } else {
                if (index > -1) {
                    currentSelected.splice(index, 1);
                } else {
                    currentSelected.push(serviceId);
                }
            }
        },

        selectPackage(packageName) {
            if (this.selectedPackage === packageName) {
                this.selectedPackage = null;
                this.selectedServices[this.currentTab] = [];
            } else {
                if (this.selectedPackage && this.currentFuneralType !== this.lastFuneralTypeForPackage) {
                    this.selectedPackage = null;
                }
                
                this.selectedPackage = packageName;
                this.lastFuneralTypeForPackage = this.currentFuneralType;
                
                this.$nextTick(() => {
                    const totalSection = document.getElementById('totalSection');
                    if (totalSection) {
                        totalSection.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'center' 
                        });
                    }
                });
            }
        },

        getSelectedPackageName() {
            const names = {
                basic: 'Базовый',
                optimal: 'Оптимальный',
                extended: 'Расширенный'
            };
            return names[this.selectedPackage] || '';
        },

        get currentFuneralType() {
            return this.currentTab === 'cremation' ? 'cremation' : 'burial';
        },

        get currentPackagePrices() {
            return this.currentFuneralType === 'cremation' 
                ? this.PACKAGE_PRICES_CREMATION 
                : this.PACKAGE_PRICES_BURIAL;
        },

        get currentPackageServices() {
            return this.currentFuneralType === 'cremation' 
                ? this.PACKAGE_SERVICES_CREMATION 
                : this.PACKAGE_SERVICES_BURIAL;
        },

        getSelectedPackageName() {
            const names = {
                basic: 'Базовый',
                optimal: 'Оптимальный',
                extended: 'Расширенный'
            };
            return names[this.selectedPackage] || '';
        },

        getSelectedPackageServices() {
            if (!this.selectedPackage) return [];
            return this.currentPackageServices[this.selectedPackage] || [];
        },

        getSelectedPackagePrice() {
            if (!this.selectedPackage) return 0;
            return this.currentPackagePrices[this.selectedPackage] || 0;
        },

        getSelectedServicesList() {
            let servicesList = [];
            
            if (this.selectedPackage) {
                servicesList = this.getSelectedPackageServices().map(name => ({
                    id: 'package_' + name.replace(/\s+/g, '_'),
                    name: name,
                    price: 0 
                }));
            } else {
                const selectedIds = this.selectedServices[this.currentTab];
                
                this.allCategories.forEach(category => {
                    category.services.forEach(service => {
                        if (selectedIds.includes(service.id)) {
                            servicesList.push({
                                id: service.id,
                                name: service.name,
                                price: parseFloat(service.price)
                            });
                        }
                    });
                });
            }
            
            if (this.getAutopsyPrice() > 0) {
                const autopsyName = this.formData.autopsyType === 'queue' 
                    ? 'Вскрытие очередное' 
                    : 'Вскрытие в день обращения';
                
                servicesList.unshift({
                    id: 'autopsy_' + this.formData.autopsyType,
                    name: autopsyName,
                    price: this.getAutopsyPrice()
                });
            }
            
            return servicesList;
        },

        calculateTotal() {
            let total = 0;
            const currentSelected = this.selectedServices[this.currentTab];

            if (this.selectedPackage) {
                total = this.getSelectedPackagePrice();
            } else {
                this.allCategories.forEach(category => {
                    category.services.forEach(service => {
                        if (currentSelected.includes(service.id)) {
                            total += parseFloat(service.price);
                        }
                    });
                });
            }

            total += this.getAutopsyPrice();

            return total;
        },

        getAutopsyPrice() {
            if (this.formData.autopsyType === 'queue') {
                return this.AUTOPSY_QUEUE_PRICE;  // 8900 ₽
            }
            if (this.formData.autopsyType === 'same_day') {
                return this.AUTOPSY_SAME_DAY_PRICE;  // 16550 ₽
            }
            return 0; 
        },

        formatPrice(price) {
            return new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB',
                minimumFractionDigits: 0
            }).format(price);
        },

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

        validateMinimumServices() {
            // Если выбран пакет - всё ок
            if (this.selectedPackage) {
                this.errors.services = '';
                return true;
            }
            
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
            if (this.selectedPackage) {
                if (!this.formData.name.trim()) return false;
                if (!this.validatePhone()) return false;
                if (!this.formData.consent) return false;  
                return true;
            }
            
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
            if (!this.formData.consent) return false; 

            return true;
        },

        // Подсказка почему кнопка неактивна
        getSubmitHint() {
            const currentSelected = this.selectedServices[this.currentTab];

            if (currentSelected.length === 0) {
                return 'Выберите хотя бы одну услугу';
            }

            if (this.currentTab === 'new' || this.currentTab === 'relative') {
                const hasCoffin = this.allCategories
                    .find(cat => cat.id === 1)?.services
                    .some(s => currentSelected.includes(s.id));
                if (!hasCoffin) {
                    return 'Для захоронения обязательно выберите гроб';
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
                    return 'Для кремации обязательно выберите гроб';
                }
                if (!hasCremation) {
                    return 'Для кремации обязательно выберите услугу кремации';
                }
            }

            if (!this.formData.name.trim()) {
                return 'Введите ваше имя';
            }

            if (!this.validatePhone()) {
                return 'Введите корректный номер телефона';
            }

            return '';
        },

        // Отправка заявки
        async submitLead() {
            this.errors.name = '';
            this.errors.phone = '';
            this.errors.services = '';
            this.errors.consent = ''; 

            if (!this.formData.name.trim()) {
                this.errors.name = 'Введите ваше имя';
                return;
            }

            if (!this.validatePhone()) {
                return;
            }

            // Проверка согласия на обработку ПДн
            if (!this.formData.consent) {
                this.errors.consent = 'Необходимо согласие на обработку персональных данных';
                return;
            }

            if (!this.selectedPackage && !this.validateMinimumServices()) {
                return;
            }

            this.submitting = true;

            let servicesToSend = [...this.selectedServices[this.currentTab]];
            
            if (this.selectedPackage && servicesToSend.length === 0) {
                servicesToSend = ['package_' + this.selectedPackage];
            }
            if (this.getAutopsyPrice() > 0) {
                servicesToSend.unshift('autopsy_' + this.formData.autopsyType);
            }
            const leadData = {
                client_name: this.formData.name.trim(),
                phone: this.formData.phone.replace(/\D/g, ''),
                funeral_type: this.currentTab,
                autopsy_type: this.formData.autopsyType, 
                selected_services: servicesToSend,
                estimated_total: this.calculateTotal(),
                comment: this.formData.comment.trim(),
                package_name: this.selectedPackage,
                consent_given: true 
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

        getTabletServices(type) {
            const category = this.allCategories.find(cat => cat.name.includes('Табличк'));
            if (!category) return [];
            
            return category.services.filter(service => {
                if (type === 'plastic') {
                    return service.name.toLowerCase().includes('пластик') || 
                        service.name.toLowerCase().includes('пластиков');
                } else if (type === 'metal') {
                    return service.name.toLowerCase().includes('металл') || 
                        service.name.toLowerCase().includes('металлическ');
                }
                return true;
            });
        },

        // Сброс формы
        resetForm() {
            this.submitSuccess = false;
            this.leadId = null;
            this.formData.name = '';
            this.formData.phone = '';
            this.formData.comment = '';
            this.formData.autopsyType = 'queue'; 
            this.formData.consent = false;  
            this.selectedPackage = null;
            this.selectedServices = {
                new: [],
                relative: [],
                cremation: []
            };
            this.currentTab = 'new';
            this.errors.services = '';
            this.errors.consent = '';  
        }
    }
}

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
