# 🗺️ GPS em Python utilizando o algoritmo A*

Projeto de um **GPS** feito em Python, utilizando conceitos de **Programação Orientada a Objetos (POO) e o algoritmo A Estrela**, utilizado como base o mapa do municipio de Santa Rosa-RS para testes.

---

# 🚀 Busca A* – Rota Curta vs Rota Demorada

Este projeto implementa o algoritmo **A\*** para encontrar a **rota mais curta** em um mapa, considerando **rotas rápidas** e **rotas demoradas**.

---

## 📌 Objetivo
O objetivo é demonstrar como a **Inteligência Artificial** pode ser aplicada na resolução de problemas de caminho ótimo, como acontece em:
- GPS (trânsito, estradas fechadas)
- Jogos digitais (movimentação de personagens)
- Robótica e logística

---

## 🧠 Método Utilizado
O algoritmo usado foi o **A\***, que calcula o custo de cada caminho atraves da formula:
f(n) = g(n) + h(n)
- `g(n)` → custo acumulado até o nó atual  
- `h(n)` → estimativa da distância até o destino 
