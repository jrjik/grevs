function contactForm() {
    return {
        submitSuccess: false,  
        
        formData: {
            name: '',
            phone: '',
            message: '',
            consent: false  
        },
        errors: {
            name: '',
            phone: '',
            consent: ''
        },
        submitting: false,

        formatPhone() {
            const value = this.formData.phone.replace(/\D/g, '');
            if (value.length === 0) {
                this.formData.phone = '';
                return;
            }

            let formatted = '+7';
            if (value[0] === '8') {
                value[0] = '7';
            }

            if (value.length > 1) formatted += ' (' + value.slice(1, 4);
            if (value.length > 4) formatted += ') ' + value.slice(4, 7);
            if (value.length > 7) formatted += '-' + value.slice(7, 9);
            if (value.length > 9) formatted += '-' + value.slice(9, 11);

            this.formData.phone = formatted;
        },

        validate() {
            let isValid = true;

            if (!this.formData.name.trim()) {
                this.errors.name = 'Введите ваше имя';
                isValid = false;
            } else {
                this.errors.name = '';
            }

            const phoneDigits = this.formData.phone.replace(/\D/g, '');
            if (phoneDigits.length < 11) {
                this.errors.phone = 'Введите полный номер телефона';
                isValid = false;
            } else {
                this.errors.phone = '';
            }

            if (!this.formData.consent) {
                this.errors.consent = 'Необходимо согласие на обработку персональных данных';
                isValid = false;
            } else {
                this.errors.consent = '';
            }

            return isValid;
        },

        async submitForm() {
            if (!this.validate()) {
                return;
            }

            this.submitting = true;

            const callbackData = {
                client_name: this.formData.name.trim(),
                phone: this.formData.phone.replace(/\D/g, ''),
                message: this.formData.message.trim(),
                consent_given: this.formData.consent,
                source: 'contacts'
            };

            try {
                const response = await fetch('/api/orders/callback/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify(callbackData)
                });

                const result = await response.json();

                if (result.status === 'success') {
                    this.submitSuccess = true;
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

        resetForm() {
            this.submitSuccess = false;
            this.formData = { name: '', phone: '', message: '', consent: false };
            this.errors = { name: '', phone: '', consent: '' };
        },

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
        }
    }
}
