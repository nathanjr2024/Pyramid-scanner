# Varredura da Pirâmide de Testes — Guia para o Estagiário

## Visão geral

A ferramenta varre todos os repositórios de microsserviços, classifica cada teste por camada e gera uma visão consolidada da pirâmide de testes de toda a organização — não uma pirâmide por serviço, mas um panorama único.

Ela roda na pipeline e produz dois artefatos:

1. Um arquivo JSON com os números da pirâmide (contagem e percentual de testes unitários, de integração e end-to-end).
2. Um arquivo HTML navegável, com a pirâmide desenhada no topo e, abaixo, um catálogo em linguagem natural de cada teste existente.

O catálogo é o diferencial: em vez de listar nomes de métodos, ele mostra a descrição legível de cada teste — o `@DisplayName` no Java, o texto dos `describe` e `it` no front. Assim, um PO ou analista de negócio abre o HTML e entende frases como "validando campos obrigatórios da tela", sem precisar ler código.

Escopo desta primeira versão: contagem da pirâmide mais o catálogo descritivo. Testes de contrato ficam de fora por enquanto.

## Stack técnica recomendada

Linguagem do script: **Python**. É fácil de ler para um estagiário, tem ótima manipulação de arquivos e texto, e boas bibliotecas para entender código de verdade.

O ponto-chave é não depender só de expressão regular. Em vez disso, usamos um *parser de árvore sintática*, que entende a estrutura do código e acha a anotação `@DisplayName` de forma confiável, mesmo quando ela está quebrada em várias linhas.

Parser por linguagem:

- **Java:** `javalang` (puro Python, simples) ou `tree-sitter` com a gramática de Java.
- **Node e Angular (JavaScript/TypeScript):** `tree-sitter` com as gramáticas de JS/TS, ou o próprio compilador do TypeScript chamado via Node.

Sugestão prática: usar `tree-sitter` para as três linguagens dá uma base única e consistente, com uma gramática por linguagem.

Onde roda: um job na pipeline (GitLab CI, GitHub Actions ou Jenkins) que clona ou acessa cada repositório, executa o script e publica os dois artefatos (JSON e HTML).

## Como funciona passo a passo

1. **Varredura.** O script recebe uma lista de repositórios e varre as pastas procurando arquivos de teste. No Java, arquivos terminados em `Test.java` ou `IT.java`; no front e no Node, arquivos `.spec` e `.test`.
2. **Classificação por camada.** Para cada arquivo ou caso de teste, decide se é unitário, de integração ou end-to-end, com base nas convenções da próxima seção.
3. **Extração da descrição.** O parser pega o `@DisplayName` no Java e os textos de `describe` e `it` no front, montando o catálogo em linguagem natural.
4. **Agregação.** Soma tudo num total geral da organização e calcula as proporções, por exemplo 65% unitário, 25% integração, 10% end-to-end.
5. **Saída.** Gera o JSON com os números e o HTML com a pirâmide visual no topo e o catálogo navegável embaixo.

## Convenções de classificação por camada

A classificação depende de regras que a equipe define. Estas são um ponto de partida — ajustem conforme os padrões de vocês.

| Camada | Java | Node / Angular |
| --- | --- | --- |
| Unitário | Arquivo `*Test.java` sem contexto de Spring | `*.spec.ts` / `*.test.ts` com Jest, sem subir app |
| Integração | Sufixo `*IT.java` ou anotação `@SpringBootTest` / `@DataJpaTest` | Testes que sobem módulo ou chamam API real (Supertest, TestBed completo) |
| End-to-end | (raro no back) | Cypress ou Playwright |

Regra de desempate: se nada indica integração ou end-to-end, cai como unitário. Vale deixar essas regras num arquivo de configuração, para ajustar sem mexer no código.

## Exemplo de HTML de saída (pirâmide + catálogo)

O HTML tem duas partes: a pirâmide desenhada no topo e o catálogo navegável embaixo. A pirâmide são três faixas empilhadas (CSS puro, sem biblioteca), cada uma mostrando contagem e percentual da camada. O catálogo agrupa os testes por serviço, com uma etiqueta colorida indicando a camada, e tem um campo de busca que filtra as frases em tempo real.

Como fica na tela:

```
            ┌────────────────────┐
            │  E2E · 48 (10%)    │
        ┌───┴────────────────────┴───┐
        │  Integração · 120 (25%)    │
   ┌────┴────────────────────────────┴────┐
   │       Unitário · 312 (65%)           │
   └──────────────────────────────────────┘

   [ Buscar teste...                       ]

   servico-pagamentos
     [Unitário]    Validando campos obrigatórios da tela
     [Unitário]    Calculando desconto acima de mil reais
     [Integração]  Persistindo pedido no banco

   portal-cliente (Angular)
     [Unitário]    Exibe erro quando CPF é inválido
     [E2E]         Cliente finaliza compra com cartão
```

Código completo (pode salvar como `piramide.html` e abrir no navegador para ver funcionando):

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pirâmide de Testes</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f5f4ef; margin: 0; padding: 2rem 1rem; color: #2c2c2a; }
    .card { max-width: 720px; margin: 0 auto; background: #fff; border: 1px solid #e3e1d8; border-radius: 12px; padding: 1.5rem; }
    h1 { font-size: 20px; font-weight: 500; margin: 0 0 4px; }
    .sub { font-size: 13px; color: #5f5e5a; margin: 0 0 1.5rem; }
    .piramide { display: flex; flex-direction: column; align-items: center; gap: 4px; margin-bottom: 1.5rem; }
    .faixa { text-align: center; padding: 10px 0; border-radius: 8px; font-size: 14px; }
    .faixa b { font-weight: 500; }
    .e2e   { background: #FAECE7; color: #712B13; }
    .integ { background: #FAEEDA; color: #633806; }
    .unit  { background: #E1F5EE; color: #085041; }
    input[type=search] { width: 100%; box-sizing: border-box; padding: 8px 10px; border: 1px solid #d3d1c7; border-radius: 8px; font-size: 14px; margin-bottom: 1.25rem; }
    .servico { margin-bottom: 1.25rem; }
    .servico h3 { font-size: 15px; font-weight: 500; margin: 0 0 6px; }
    .teste { display: flex; gap: 8px; align-items: center; padding: 6px 0; border-bottom: 1px solid #eee; font-size: 14px; }
    .tag { font-size: 11px; padding: 2px 8px; border-radius: 6px; white-space: nowrap; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Pirâmide de testes</h1>
    <p class="sub">Visão consolidada · 12 microsserviços · 480 testes</p>

    <!-- As larguras e os números são preenchidos pelo script a partir do JSON -->
    <div class="piramide">
      <div class="faixa e2e"   style="width: 34%"><b>E2E</b> · 48 (10%)</div>
      <div class="faixa integ" style="width: 64%"><b>Integração</b> · 120 (25%)</div>
      <div class="faixa unit"  style="width: 94%"><b>Unitário</b> · 312 (65%)</div>
    </div>

    <input type="search" id="busca" placeholder="Buscar teste">

    <div id="catalogo">
      <div class="servico">
        <h3>servico-pagamentos</h3>
        <div class="teste"><span class="tag unit">Unitário</span>Validando campos obrigatórios da tela</div>
        <div class="teste"><span class="tag unit">Unitário</span>Calculando desconto acima de mil reais</div>
        <div class="teste"><span class="tag integ">Integração</span>Persistindo pedido no banco</div>
      </div>
      <div class="servico">
        <h3>portal-cliente (Angular)</h3>
        <div class="teste"><span class="tag unit">Unitário</span>Exibe erro quando CPF é inválido</div>
        <div class="teste"><span class="tag e2e">E2E</span>Cliente finaliza compra com cartão</div>
      </div>
    </div>
  </div>

  <script>
    document.getElementById('busca').addEventListener('input', function (e) {
      var q = e.target.value.toLowerCase();
      document.querySelectorAll('#catalogo .teste').forEach(function (el) {
        el.style.display = el.textContent.toLowerCase().includes(q) ? 'flex' : 'none';
      });
    });
  </script>
</body>
</html>
```

Observações para o estagiário:

- Os números e frases acima são de exemplo. O script gera esse HTML com os dados reais do JSON.
- A largura de cada faixa da pirâmide pode ser fixa (visual de pirâmide) ou proporcional ao percentual — o importante é o rótulo mostrar contagem e percentual reais.
- Uma forma simples de gerar o HTML em Python é usar um template com `Jinja2`.

## Faseamento sugerido

Para o estagiário entregar em partes e não travar:

1. **Fase 1 — Contagem só no Java.** Varrer um repositório, contar arquivos de teste por camada e imprimir os números no terminal. Sem parser ainda, só por nome de arquivo.
2. **Fase 2 — JSON consolidado.** Estender para vários repositórios e gerar o JSON com o total geral e as proporções.
3. **Fase 3 — HTML com a pirâmide.** Ler o JSON e gerar o HTML com as três faixas (usar o exemplo acima como base).
4. **Fase 4 — Extração de descrições no Java.** Entrar o parser para ler o `@DisplayName` e montar o catálogo.
5. **Fase 5 — Node e Angular.** Repetir a varredura, a classificação e a extração de `describe`/`it` para o front.
6. **Fase 6 — Integração na pipeline.** Rodar como job e publicar os artefatos.

Cada fase entrega algo utilizável por si só, o que facilita revisar o trabalho e corrigir o rumo cedo.
