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

        // Obter o userId do campo oculto
        const userId = document.getElementById('user-id').value;

        // Fazer uma requisição POST para criar uma sessão de checkout
        fetch("/subscriptions/create-checkout-session/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                priceId: priceId,
                priceValue: priceValue,
                clientReferenceId: userId,
                csrfmiddlewaretoken: csrftoken,
            }),
        })
        .then(function(response) {
            // Log para verificar a resposta da requisição
            console.log("Resposta da requisição:", response);

            // Verificar se a resposta da requisição é ok
            if (!response.ok) {
                return response.json().then(function(error) {
                    throw new Error(error.error);
                });
            }
            return response.json();
        })
        .then(function(session) {
            // Log para verificar a sessão recebida
            console.log("Sessão recebida:", session);

            // Redirecionar para a página de checkout do Stripe
            if (session.id) {
                return stripe.redirectToCheckout({ sessionId: session.id });
            } else {
                throw new Error('ID da sessão não retornado.');
            }
        })
        .catch(function(error) {
            // Log para capturar erros
            console.error("Erro:", error);

            // Improved error handling
            if (error.message) {
                alert(error.message);
            } else {
                alert("Ocorreu um erro durante o checkout. Por favor, tente novamente.");
            }
        });

    };
});
