// db-container/init-mongo.js
// MongoDB initialization script that runs when the container starts

// Switch to the 'together' database (creates it if it doesn't exist)
db = db.getSiblingDB('together');

// Create collections
db.createCollection('users');
db.createCollection('events');
db.createCollection('messages');

// Create indexes for better query performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.events.createIndex({ "user_id": 1 });
db.events.createIndex({ "start_time": 1 });
db.messages.createIndex({ "sender_id": 1 });
db.messages.createIndex({ "receiver_id": 1 });

// Insert sample user (optional, for testing)
try {
  db.users.insertOne({
    name: "Test User",
    email: "test@example.com",
    password_hash: "$2b$12$K8PVqOGX9jCNSvv3xM2qZ.TQP0XR.fjrLPJYEIfMEmMuGTzwYMj2m", // Password: password123
    created_at: new Date()
  });
  print("Created test user: test@example.com / password123");
} catch (e) {
  print("Test user already exists or could not be created: " + e.message);
}

print("MongoDB initialization complete!");
