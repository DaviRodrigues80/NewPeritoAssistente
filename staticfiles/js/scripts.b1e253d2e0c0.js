console.log('Script carregado!');



document.addEventListener('DOMContentLoaded', function() {
    // Função auxiliar para obter o valor do token CSRF
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : null;
    }

    const csrftoken = getCSRFToken();
    console.log('CSRF Token:', csrftoken);


    // Verificar se a chave de publicação do Stripe está definida
    const stripePublishableKey = document.querySelector('meta[name="stripe-key"]').getAttribute('content');
    if (!stripePublishableKey) {
        console.error("STRIPE_PUBLISHABLE_KEY não está definida");
        return;
    }

    // Inicializar Stripe
    const stripe = Stripe(stripePublishableKey);

    // Função para iniciar o checkout
    window.checkout = function(priceId, priceElementId) {
        var priceText = document.getElementById(priceElementId).innerText;
        var priceValue = parseFloat(priceText.replace('R$', '').replace(',', '.'));

        // Fazer uma requisição POST para criar uma sessão de checkout
        fetch("/subscriptions/create-checkout-session/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": 'csrftoken',
            },
            body: JSON.stringify({
                priceId: priceId,
                priceValue: priceValue
            }),
        })
        .then(function(response) {
            // Verificar se a resposta da requisição é ok
            if (!response.ok) {
                return response.json().then(function(error) {
                    throw new Error(error.error);
                });
            }
            return response.json();
        })
        .then(function(session) {
            // Redirecionar para a página de checkout do Stripe
            if (session.id) {
                return stripe.redirectToCheckout({ sessionId: session.id });
            } else {
                throw new Error('ID da sessão não retornado.');
            }
        })
        .catch(function(error) {
            // Improved error handling
            console.error("Erro:", error);
            if (error.message) {
              alert(error.message);
            } else {
              alert("Ocorreu um erro durante o checkout. Por favor, tente novamente.");
            }
        });
    };
});

// Função auxiliar para obter o valor do token CSRF
function getCookie(name) {
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

const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});