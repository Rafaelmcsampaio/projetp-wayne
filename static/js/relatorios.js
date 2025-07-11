// projetp-wayne/static/js/relatorios.js

document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('dataChart'); 
    if (!canvas) {
        console.warn("Elemento canvas com id 'dataChart' não encontrado. O gráfico de relatórios não será renderizado.");
        return; 
    }

    const totalAlertas = parseInt(canvas.getAttribute('data-total-alertas'), 10);
    const alertasCriticos = parseInt(canvas.getAttribute('data-alertas-criticos'), 10);
    const totalRecursos = parseInt(canvas.getAttribute('data-total-recursos'), 10);
    const totalUsuarios = parseInt(canvas.getAttribute('data-total-usuarios'), 10);
    const totalAreas = parseInt(canvas.getAttribute('data-total-areas'), 10);

    const ctx = canvas.getContext('2d');
    
    const dataChart = new Chart(ctx, {
        type: 'bar', 
        data: {
            labels: ['Total Alertas', 'Alertas Críticos', 'Recursos', 'Usuários', 'Áreas'],
            datasets: [{
                label: 'Quantidade',
                data: [
                    totalAlertas,
                    alertasCriticos,
                    totalRecursos,
                    totalUsuarios,
                    totalAreas
                ],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.7)',  
                    'rgba(231, 76, 60, 0.7)',   
                    'rgba(46, 204, 113, 0.7)',  
                    'rgba(155, 89, 182, 0.7)',  
                    'rgba(241, 196, 15, 0.7)'   
                ],
                borderColor: [
                    'rgba(52, 152, 219, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(46, 204, 113, 1)',
                    'rgba(155, 89, 182, 1)',
                    'rgba(241, 196, 15, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true, 
            maintainAspectRatio: true, /* <-- CORRIGIDO AQUI: Mantenha a proporção do canvas */
            scales: {
                y: {
                    beginAtZero: true,
                    precision: 0, 
                    title: {
                        display: true,
                        text: 'Contagem'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Categorias'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false 
                },
                title: {
                    display: true,
                    text: 'Visão Geral dos Dados do Sistema'
                }
            }
        }
    });
});