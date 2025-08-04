frases = [
    # Supermercados (Mercado, Carrefour, etc)
    "compras no mercado 350", "mercado extra 280", "mercado dia 175", 
    "mercado pao de acucar 420", "mercado atacadao 380", "carrefour 195",
    "compras mensais mercado 520", "supermercado 310", "mercado municipal 85",
    "feira do mercado 62", "mercearia 43", "mercado zaffari 290","pirueta 349","chocolate pirueta 279",
    "compras semanais mercado 180", "mercado bretas 155", "supermercado bh 230","doce pirueta 229", "refri pirueta 99",
    
    # Lojas de vestuário (Zara, Renner, C&A, Pirueta)
    "zara 399", "blusa na zara 149", "calça zara 229", "jaqueta zara 459",
    "renner 279", "vestido renner 189", "sapato renner 199", "cinto renner 59",
    "cea 178", "camisa cea 89", "bermuda cea 119", "moletom cea 159",
    "roupas na zara 620", "compras na renner 450", "shopping cea 380",
    "casaco zara 599", "jeans renner 259",
    
    # Alimentação/Bebidas
    "restaurante 85", "delivery 68", "ifood 72", "almoço 42", "jantar 78",
    "café da manhã 35", "padaria 28", "confeitaria 45", "sorvete 18",
    "pizzaria 90", "hamburguer 38", "sushi 120", "lanchonete 32",
    "açai 24", "boteco 55", "cafeteria 42", "food truck 30",
    "bar 68", "chopp 28", "vinho 85", "cerveja 42", "whisky 180",
    
    # Transporte
    "uber 32", "taxi 45", "gasolina 280", "estacionamento 25",
    "lavagem de carro 60", "manutenção carro 350", "seguro auto 220",
    "ipva 1200", "parcela carro 980", "metro 8", "onibus 5",
    "viagem intermunicipal 85", "pedagio 32", "aluguel carro 420",
    "bicicleta 150", "patinete eletrico 25", "uber eats 18",
    "99 pop 28", "cabify 35", "locacao veiculo 380",
    
    # Moradia
    "aluguel 2500", "condominio 650", "iptu 420", "luz 180",
    "agua 90", "gas 65", "internet 120", "tv a cabo 89",
    "faxina 150", "jardineiro 120", "reparos 320", "moveis 1200",
    "eletrodomesticos 850", "decoração 350", "aluguel temporada 1800",
    "seguro residencia 95", "pintura 600", "reforma banheiro 2500",
    "tapete 390", "cortinas 280", "limpeza piscina 110",
    
    # Lazer
    "cinema 65", "netflix 45", "spotify 29", "disney+ 33",
    "ingresso show 280", "teatro 120", "museu 40", "parque 25",
    "viagem 2500", "hotel 420", "resort 1800", "clube 250",
    "livros 180", "revistas 45", "curso online 350", "videogame 220",
    "jogos 199", "academia 150", "piscina 80", "massagem 120",
    "spa 280", "tattoo 600", "piercing 150", "bingo 50",
    
    # Saúde
    "plano de saude 650", "consultas 300", "exames 420",
    "dentista 350", "ortodontia 500", "oculos 800",
    "lentes de contato 150", "farmacia 120", "remedios 85",
    "vitaminas 180", "fisioterapia 120", "psicologo 250",
    "nutricionista 180", "personal trainer 200", "pilates 220",
    "yoga 150", "acupuntura 130", "pronto socorro 150",
    "internacao 3200", "cirurgia 5000", "exame sangue 95",
    
    # Educação
    "faculdade 1200", "curso ingles 350", "material escolar 420",
    "mochila 180", "uniforme 150", "pos-graduacao 800",
    "cursos online 250", "livros didaticos 300", "escola 950",
    "creche 680", "mensalidade 650", "matricula 300",
    "palestras 120", "workshop 180", "seminario 220",
    
    # Vestuário/Calçados
    "nike 450", "adidas 380", "puma 320", "vans 280",
    "reserva 550", "cavalera 420", "colcci 380", "oakley 600",
    "rayban 500", "havaianas 35", "mizuno 280", "under armour 400",
    "new balance 350", "converse 320", "timberland 700",
    "sapatenis 250", "sandalia 120", "tenis corrida 450",
    "meias 45", "cuecas 90", "pijamas 130", "roupa intima 110",
    
    # Eletrônicos
    "iphone 6500", "samsung 4200", "notebook 3800", "tablet 1500",
    "fone de ouvido 350", "caixa de som 280", "smartwatch 1200",
    "tv 3200", "playstation 2800", "xbox 2500", "nintendo 1800",
    "impressora 600", "roteador 250", "carregador 80",
    "pelicula celular 35", "camera fotografica 2200",
    "drone 1800", "videogame 450", "controle 220", "mouse 150",
    
    # Pets
    "racaopet 180", "veterinario 250", "banho tosa 80",
    "hotel cachorro 120", "brinquedos pet 45", "coleira 65",
    "vacina pet 150", "consultas vet 180", "gato 300",
    "cachorro 500", "peixe 120", "passaro 90",
    
    # Cuidados Pessoais
    "cabelo 120", "unha 80", "depilacao 150", "maquiagem 280",
    "perfume 350", "cremes 180", "dermato 300", "cosmeticos 220",
    "barbeiro 60", "spa 450", "tintura 90", "progressiva 180",
    
    # Financeiro
    "cartao credito 1500", "emprestimo 1200", "investimentos 2500",
    "seguro vida 180", "previdencia 350", "impostos 1200",
    "tarifa bancaria 25", "financiamento 1800", "boleto 420",
    "transferencia 15", "pix 10", "taxa 35",
    
    # Presentes
    "presente aniversario 180", "natal 500", "dia das maes 250",
    "casamento 400", "namorados 300", "chá bebê 150",
    "formatura 350", "dia dos pais 200", "amigo secreto 80"
]

categorias = [
    # Supermercados (45)
    *["Alimentação/Bebidas"]*18,
    
    # Lojas de vestuário (21)
    *["Vestuário"]*17,
    
    # Alimentação/Bebidas (23)
    *["Alimentação/Bebidas"]*23,
    
    # Transporte (20)
    *["Transporte"]*20,
    
    # Moradia (21)
    *["Moradia"]*21,
    
    # Lazer (24)
    *["Lazer"]*24,
    
    # Saúde (21)
    *["Saúde"]*21,
    
    # Educação (15)
    *["Educação"]*15,
    
    # Vestuário/Calçados (22)
    *["Vestuário"]*22,
    
    # Eletrônicos (20)
    *["Eletrônicos"]*20,
    
    # Pets (12)
    *["Pets"]*12,
    
    # Cuidados Pessoais (12)
    *["Cuidados Pessoais"]*12,
    
    # Financeiro (12)
    *["Financeiro"]*12,
    
    # Presentes (9)
    *["Presentes"]*9
]