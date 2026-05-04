--- student
INSERT INTO STUDENT
VALUES (1001, 'hashed_pw_1', '+639171111111', 'john@email.com', 'John Reyes');

INSERT INTO STUDENT
VALUES (1002, 'hashed_pw_2', '+639172222222', 'maria@email.com', 'Maria Santos');

INSERT INTO STUDENT
VALUES (1003, 'hashed_pw_3', '+639173333333', 'clara@email.com', 'Clara Dizon');

--- staff
INSERT INTO STAFF 
VALUES (7001, 'Math', 'hashed_pw_staff1', 'mr.cruz@email.com');

INSERT INTO STAFF 
VALUES (7002, 'Science', 'hashed_pw_staff2', 'ms.reyes@email.com');

INSERT INTO STAFF 
VALUES (7003, 'Computer', 'hashed_pw_staff3', 'mr.santos@email.com');

INSERT INTO STAFF 
VALUES (7004, NULL, 'hashed_pw_staff4', 'admin.staff@email.com');

--- assignment
INSERT INTO ASSIGNMENT
VALUES (2001, 'Assignment 1', 'Math', 100.00);

INSERT INTO ASSIGNMENT
VALUES (2002, 'Assignment 2', 'English', 100.00);

--- quiz
INSERT INTO QUIZ
VALUES (3001, 'Quiz 1', 'Science', 50.00);

INSERT INTO QUIZ
VALUES (3002, 'Quiz 2', 'Civics', 50.00);

--- exam
INSERT INTO EXAM
VALUES (4001, 'Midterm Exam', 'Computer', 100.00);

INSERT INTO EXAM
VALUES (4002, 'Final Exam', 'PE', 100.00);

--- enrollment
INSERT INTO ENROLLMENT
VALUES (5001, 1001, 1, '2026-06-01');

INSERT INTO ENROLLMENT
VALUES (5002, 1002, 1, '2026-06-01');

INSERT INTO ENROLLMENT
VALUES (5003, 1003, 2, '2026-06-01');

--- grade
INSERT INTO GRADE
VALUES (6001, 85.0, 88.50, 'Math', 1001, 2001, NULL, NULL);

INSERT INTO GRADE
VALUES (6002, 45.0, 90.00, 'Science', 1001, NULL, 3001, NULL);

INSERT INTO GRADE
VALUES (6003, 92.0, 92.00, 'Computer', 1002, NULL, NULL, 4001);

INSERT INTO GRADE
VALUES (6004, 78.0, 80.00, 'English', 1003, 2002, NULL, NULL);
INSERT INTO ROLE VALUES
(1,'Student'),
(2,'Admin'),
(3,'Teacher'),
(4,'Coordinator'),
(5,'Guidance Counselor');

INSERT INTO STUDENT VALUES
(1001,'Juan Dela Cruz','juan@fgiss.edu','pass123',1),
(1002,'Maria Santos','maria@fgiss.edu','pass123',1),
(1003,'Carlos Reyes','carlos@fgiss.edu','pass123',1);

INSERT INTO STAFF VALUES
(2001,'Mathematics','pass123','teacher1@fgiss.edu',3),
(2002,'Administration','pass123','admin@fgiss.edu',2),
(2003,'Guidance','pass123','counselor@fgiss.edu',5);

INSERT INTO SUBJECT VALUES
(3001,'Mathematics 1','MATH101'),
(3002,'English Literature','ENG201'),
(3003,'Introduction to Programming','CS101');

INSERT INTO CLASS VALUES
(4001,'Room101',2026),
(4002,'Room202',2026),
(4003,'ComputerLab1',2026);

INSERT INTO ENROLLMENT VALUES
(5001,1001,4001,'2026-06-01'),
(5002,1002,4002,'2026-06-01'),
(5003,1003,4003,'2026-06-01');

INSERT INTO ASSIGNMENT VALUES
(6001,'Algebra Homework',100),
(6002,'Essay Writing',100),
(6003,'Programming Exercise',100);

INSERT INTO QUIZ VALUES
(7001,'Algebra Quiz',50),
(7002,'Grammar Quiz',50),
(7003,'Programming Quiz',50);

INSERT INTO EXAM VALUES
(8001,'Midterm Exam Math',100),
(8002,'Midterm Exam English',100),
(8003,'Midterm Exam Programming',100);

INSERT INTO GRADE VALUES
(9001,85.00,88.50,1001,6001,NULL,NULL),
(9002,45.00,90.00,1001,NULL,7001,NULL),
(9003,92.00,92.00,1002,NULL,NULL,8002);

INSERT INTO SYLLABUS VALUES
(10001,30.00,40.00,30.00,3001),
(10002,25.00,50.00,25.00,3002),
(10003,20.00,50.00,30.00,3003);

INSERT INTO CLASS_SUBJECT VALUES
(11001,4001,3001,2026),
(11002,4002,3002,2026),
(11003,4003,3003,2026);

INSERT INTO CLASS_STAFF VALUES
(12001,4001,2001),
(12002,4002,2002),
(12003,4003,2003);

INSERT INTO INTERVENTION VALUES
(13001,'Low math scores','Student assigned to weekly tutoring'),
(13002,'Frequent tardiness','Student required to attend counseling'),
(13003,'Difficulty in programming','Additional lab assistance');

INSERT INTO VIOLATION VALUES
(14001,'Late to class multiple times','Tardiness','Student arrived late three times','2026-02-01 08:30:00'),
(14002,'Talking during exam','Academic Misconduct','Student caught communicating','2026-02-05 10:15:00'),
(14003,'Disruptive behavior','Classroom Misconduct','Student repeatedly interrupted lecture','2026-02-10 09:45:00');