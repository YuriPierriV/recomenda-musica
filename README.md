# 🎵 Sistema de Recomendação Musical

Este projeto implementa uma API RESTful de recomendação de músicas, utilizando **FastAPI**. A API é capaz de sugerir músicas através de métodos como **similaridade baseada em conteúdo**, **gênero/artista**, **filtro colaborativo** e **modelo híbrido**.
Além disso, músicas populares podem ser consultadas filtrando por ano ou gênero.

---

## 🚀 Funcionalidades

- Recomendação **Baseada em Conteúdo** (características musicais)
- Recomendação **por Gênero e Artista**
- **Filtro Colaborativo** (usuários fictícios)
- **Sistema Híbrido** (combina conteúdo + colaborativo)
- Consulta de **Músicas Populares** por ano/gênero

---

## 📦 Estrutura de Arquivos

```
├──music-recomendation-service/
│   ├── app/
│   │   ├── main.py
│   │   └── musicas.csv   
│   ├── Dockerfile
│   └── requirements.txt
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Como Rodar Localmente

### Pré-requisitos

- Docker e docker compose instalado

---

### 📥 1. Clone o projeto

```bash
git clone https://github.com/seu-usuario/music-recommendation-service.git
cd music-recommendation-service
```

---

### 🐳 2. Rode o docker compose

```bash
docker-compose up -d
```

---

### 3. Acesse

Acesse a API em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 📚 Documentação da API (Swagger)

Após rodar a aplicação, acesse:

- **Swagger UI** (interativo): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc** (visualização alternativa): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📬 Endpoints Disponíveis

| Método | Rota                                          | Descrição                               |
| :----- | :-------------------------------------------- | :-------------------------------------- |
| GET    | `/recommendations/content-based/{song_title}` | Recomendação por características        |
| POST   | `/recommendations/genre-artist`               | Recomendação por gênero/artista         |
| GET    | `/recommendations/collaborative/{user_id}`    | Recomendação colaborativa               |
| POST   | `/recommendations/hybrid`                     | Recomendação híbrida                    |
| GET    | `/recommendations/popular`                    | Listar músicas populares por ano/gênero |

---

## 👨‍💻 Tecnologias usadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Pandas](https://pandas.pydata.org/)
- [Scikit-learn](https://scikit-learn.org/stable/)

---

> Desenvolvido para fins acadêmicos e estudo de APIs de recomendação.

---

# 🎵 Obrigado!

---
