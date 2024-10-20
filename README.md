# School Library Network Management System

## I. Project Overview

This project aims to create a comprehensive **School Library Management System** for public schools. The system will manage all necessary information for operating a school library, ensuring every school with a library can meet the technological requirements for efficient operations. The application will be accessible to all public schools, allowing school library operators to manage the catalog of available books and library functions seamlessly.

## II. Features

### 1. School Management
Each school operating the library will register the following details:
- **School Name**
- **Address**
- **City**
- **Phone Number**
- **Email**
- **School Director Name**
- **School Library Operator Name**

Each school is responsible for registering its library's available books in the system.

### 2. Book Management
The system will handle book information, including:
- **Title**
- **Publisher**
- **ISBN**
- **Authors** (one or more)
- **Number of Pages**
- **Summary**
- **Available Copies (Inventory)**
- **Book Image**
- **Thematic Category** (one or more)
- **Language**
- **Keywords**

### 3. User Roles & Authentication
Users must log in with a **username** and **password**. The system supports the following roles:
- **Network School Library Administrator (Administrator):** 
  - Registers schools and approves/appoints library operators.
  - Manages backups and restoration of the database.
- **School Library Operator:**
  - Manages book data, reservations, loans, and returns.
  - Approves user registrations, prints borrower cards, and supervises loans.
- **Students and Teachers:**
  - Register through the system and require operator approval.
  - Can view and borrow books, request reservations, and leave reviews.

### 4. Borrowing & Reservations
- **Borrowing Rules:**
  - Students can borrow up to 2 books per week.
  - Teachers can borrow 1 book per week.
  - Operators manage the borrowing and returning process.
- **Reservations:**
  - Users can reserve books, limited to their weekly borrowing capacity.
  - Reservations expire after 1 week if unfulfilled.

### 5. Reviews & Ratings
- Users can submit written **reviews** and rate books on a **Likert scale**. 
- Student reviews require approval from the library operator.

### 6. CRUD Operations
All users have the ability to manage information (search, update, delete) using the system's **CRUD** functionalities.

## III. Database and Queries

### 1. ER Diagram & Relational Diagram
The project requires designing the **ER diagram** and **relational database schema** to store school, book, and user data.

### 2. Database Implementation
- **DDL & DML Scripts**: Create tables, insert data.
- **Constraints**: Ensure database integrity with appropriate constraints (keys, referential integrity, etc.).
- **Indexes**: Define indexes to optimize database performance.
  
The database should contain sample data for testing: 
- 3 schools
- 100 books
- 50 loans
- 40 reservations
- 30 students
- 10 teachers

### 3. Sample Queries
The system will include queries for:
- **Administrator**: 
  - List loans by school, find popular authors, track borrowing patterns, etc.
- **Operator**: 
  - Search for books, track delayed returns, analyze user ratings.
- **User**: 
  - View available books, list books borrowed by the user.

## IV. User Interface (UI)

The application features a user-friendly interface with practical forms and elements (drop-downs, radio buttons, etc.) to manage all operations without requiring users to know SQL or database mechanics.

## V. User Manual

A detailed **user manual** in PDF format will guide users through the system's functionalities, including managing books, users, and loans.
