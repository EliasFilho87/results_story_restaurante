# -*- coding: utf-8 -*-
"""
Storytelling de Dados — "Se a loja fosse um restaurante…"
Autor: Elias Filho

O script:
- Lê CSVs (orders, order_items, products, customers)
- Calcula os 4 "personagens": Prato do Dia, Item Gourmet, Mesa Cativa, Café
- Imprime um texto explicativo
- Gera gráficos em PNG e um markdown com a história
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from textwrap import dedent

# ---------- Helpers ----------
def brl(v):
    # formata no estilo brasileiro: R$ 1.234,56
    s = f"R$ {float(v):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# caminhos
ROOT = os.path.dirname(os.path.dirname(__file__)) if "__file__" in globals() else "."
CSV = lambda name: os.path.join(ROOT, name)
OUT_DIR = os.path.join(ROOT, "results_story_restaurante")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Carregar dados ----------
orders = pd.read_csv(CSV("orders.csv"))
order_items = pd.read_csv(CSV("order_items.csv"))
products = pd.read_csv(CSV("products.csv"))
customers = pd.read_csv(CSV("customers.csv"))

# considerar apenas pedidos concluídos
orders_ok = orders[orders["status"] == "Concluído"].copy()

# join 
df = order_items.merge(products, on="product_id").merge(orders_ok, on="order_id", how="inner")
df["revenue"] = df["quantity"] * df["selling_price"]

# ---------- Métricas principais ----------
# 🍔 Prato do Dia: produto mais vendido (em quantidade)
qty_by_product = df.groupby("name")["quantity"].sum().sort_values(ascending=False)
prato_nome = qty_by_product.index[0]
prato_qty = int(qty_by_product.iloc[0])

# 🥂 Item Gourmet: maior ticket médio por pedido onde o produto aparece
order_rev = (
    df.groupby(["order_id", "name"])["revenue"]
      .sum()
      .reset_index()
)
ticket_medio_by_product = order_rev.groupby("name")["revenue"].mean().sort_values(ascending=False)
gourmet_nome = ticket_medio_by_product.index[0]
gourmet_ticket = float(ticket_medio_by_product.iloc[0])

# 🍻 Cliente da Mesa Cativa: cliente com mais pedidos concluídos
orders_per_customer = orders_ok.groupby("customer_id")["order_id"].nunique().sort_values(ascending=False)
mesa_cativa_id = int(orders_per_customer.index[0])
mesa_cativa_pedidos = int(orders_per_customer.iloc[0])
customers["customer_id"] = customers["customer_id"].astype(int)
mesa_cativa_nome = customers.loc[customers["customer_id"] == mesa_cativa_id, "name"].values[0]

# ☕ Os que só vieram pelo café: clientes com exatamente 1 pedido
cafe_qtd = int((orders_per_customer == 1).sum())
total_clientes = int(orders_per_customer.shape[0])
cafe_pct = (100 * cafe_qtd / total_clientes) if total_clientes else 0

# ---------- Texto explicativo (terminal + markdown) ----------
story = dedent(f"""
🍽️ Se a loja fosse um restaurante…

🍔 Prato do Dia: {prato_nome} — {prato_qty} unidades vendidas
👉 O item mais popular do cardápio, presente em muitos pedidos.

🥂 Item Gourmet: {gourmet_nome} — ticket médio por pedido {brl(gourmet_ticket)}
👉 Aparece menos, mas quando vem, eleva o valor da conta.

🍻 Cliente da Mesa Cativa: {mesa_cativa_nome} (ID {mesa_cativa_id}) — {mesa_cativa_pedidos} pedidos
👉 O cliente fiel, que voltou várias vezes e já é quase de casa.

☕ Clientes de 1 compra só: {cafe_qtd} ({cafe_pct:.1f}%)
👉 A turma que passou para um café, mas não voltou para o almoço.

(Período: 2025-01 a 2025-08 — apenas pedidos "Concluído")
""").strip()

print(story)

# também salva em markdown para usar no README/link do GitHub
with open(os.path.join(OUT_DIR, "story_restaurante.md"), "w", encoding="utf-8") as f:
    f.write("# 🍽️ Se a loja fosse um restaurante…\n\n")
    f.write(story.replace("\n\n", "\n\n") + "\n")

# ---------- Gráficos ----------
# Top 7 por quantidade (Prato do Dia)
top_qty = qty_by_product.head(7)[::-1]  # invertido para gráfico horizontal
plt.figure(figsize=(9, 5))
top_qty.plot(kind="barh")
plt.title("Top produtos por quantidade (Prato do Dia)")
plt.xlabel("Unidades vendidas")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "top_qty_products.png"), dpi=160, bbox_inches="tight")
plt.close()

# Top 7 por ticket médio (Item Gourmet)
top_ticket = ticket_medio_by_product.head(7)[::-1]
plt.figure(figsize=(9, 5))
top_ticket.plot(kind="barh")
plt.title("Top produtos por ticket médio (Item Gourmet)")
plt.xlabel("Ticket médio por pedido (R$)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "top_ticket_products.png"), dpi=160, bbox_inches="tight")
plt.close()
