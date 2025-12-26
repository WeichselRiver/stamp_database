# Stamp Database API

A simple Flask REST API for managing stamp collections with data stored in Parquet format.

## Features

- Create, Read, Update, and Delete (CRUD) operations for stamps
- Data persistence using Apache Parquet format via Polars
- RESTful API endpoints
- Automatic ID generation
- High-performance data operations with Polars

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the Flask development server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Get All Stamps
```
GET /stamps
```
Returns a list of all stamps in the database.

**Example Response:**
```json
[
  {
    "database_id": 1,
    "katalog_id": "Michel 123",
    "Gebiet": "USA",
    "jahr": 1995,
    "nennwert": "32 cents",
    "beschreibung": "Liberty Bell",
    "zustand": "Mint"
  }
]
```

### Get a Specific Stamp
```
GET /stamps/<id>
```
Returns details of a single stamp by ID.

### Create a New Stamp
```
POST /stamps
Content-Type: application/json
```

**Required Fields:**
- `Gebiet`: Geographic area/region (Gebiet)
- `jahr`: Year of issue (Jahr)
- `nennwert`: Stamp value/denomination (Nennwert)

**Optional Fields:**
- `katalog_id`: Catalog reference ID (Katalog-ID)
- `beschreibung`: Description of the stamp (Beschreibung)
- `zustand`: Condition of the stamp (Zustand)

**Example Request:**
```json
{
  "katalog_id": "Michel 123",
  "Gebiet": "USA",
  "jahr": 1995,
  "nennwert": "32 cents",
  "beschreibung": "Liberty Bell",
  "zustand": "Mint"
}
```

### Update a Stamp
```
PUT /stamps/<id>
Content-Type: application/json
```

**Example Request:**
```json
{
  "zustand": "Used",
  "beschreibung": "Updated description"
}
```

### Delete a Stamp
```
DELETE /stamps/<id>
```

## Data Storage

Stamp data is stored in `stamps.parquet` file in the root directory using Polars. This provides:
- Efficient columnar storage with Parquet format
- Blazing fast read/write operations powered by Polars
- Excellent compression
- Type safety and memory efficiency
- High-performance query operations

## Example Usage with curl

**Create a stamp:**
```bash
curl -X POST http://localhost:5000/stamps \
  -H "Content-Type: application/json" \
  -d '{"katalog_id": "Michel 123", "Gebiet": "USA", "jahr": 1995, "nennwert": "32 cents", "beschreibung": "Liberty Bell", "zustand": "Mint"}'
```

**Get all stamps:**
```bash
curl http://localhost:5000/stamps
```

**Get a specific stamp:**
```bash
curl http://localhost:5000/stamps/1
```

**Update a stamp:**
```bash
curl -X PUT http://localhost:5000/stamps/1 \
  -H "Content-Type: application/json" \
  -d '{"zustand": "Used"}'
```

**Delete a stamp:**
```bash
curl -X DELETE http://localhost:5000/stamps/1
```

## Data Schema

| Field | Type | Description |
|-------|------|-------------|
| database_id | Integer | Auto-generated unique identifier |
| katalog_id | String | Catalog reference ID (Katalog-ID) |
| Gebiet | String | Geographic area/region (Gebiet) |
| jahr | Integer | Year of issue (Jahr) |
| nennwert | String | Stamp value/denomination (Nennwert) |
| beschreibung | String | Description of the stamp (Beschreibung) |
| zustand | String | Condition (Zustand - Mint, Used, etc.) |
