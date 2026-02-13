import { Client } from "pg";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    
    const client = new Client({ connectionString: env.HYPERDRIVE.connectionString });
    await client.connect();

    try {
      // CREATE
      if (method === "POST" && path === "/items") {
        const { name } = await request.json();
        const result = await client.query(
          "INSERT INTO test_items (name) VALUES ($1) RETURNING *",
          [name]
        );
        return Response.json({ action: "created", item: result.rows[0] });
      }

      // READ all
      if (method === "GET" && path === "/items") {
        const result = await client.query("SELECT * FROM test_items ORDER BY id");
        return Response.json({ action: "list", count: result.rows.length, items: result.rows });
      }

      // READ one
      if (method === "GET" && path.startsWith("/items/")) {
        const id = path.split("/")[2];
        const result = await client.query("SELECT * FROM test_items WHERE id = $1", [id]);
        if (result.rows.length === 0) {
          return Response.json({ error: "not found" }, { status: 404 });
        }
        return Response.json({ action: "get", item: result.rows[0] });
      }

      // UPDATE
      if (method === "PUT" && path.startsWith("/items/")) {
        const id = path.split("/")[2];
        const { name } = await request.json();
        const result = await client.query(
          "UPDATE test_items SET name = $1 WHERE id = $2 RETURNING *",
          [name, id]
        );
        if (result.rows.length === 0) {
          return Response.json({ error: "not found" }, { status: 404 });
        }
        return Response.json({ action: "updated", item: result.rows[0] });
      }

      // DELETE
      if (method === "DELETE" && path.startsWith("/items/")) {
        const id = path.split("/")[2];
        const result = await client.query("DELETE FROM test_items WHERE id = $1 RETURNING *", [id]);
        if (result.rows.length === 0) {
          return Response.json({ error: "not found" }, { status: 404 });
        }
        return Response.json({ action: "deleted", item: result.rows[0] });
      }

      return Response.json({ 
        usage: {
          "POST /items": "Create item: {name: 'test'}",
          "GET /items": "List all items",
          "GET /items/:id": "Get one item",
          "PUT /items/:id": "Update item: {name: 'new'}",
          "DELETE /items/:id": "Delete item"
        }
      });

    } finally {
      await client.end();
    }
  },
};
