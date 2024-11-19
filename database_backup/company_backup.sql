CREATE TABLE `roles` (
  `role_pk` char(36) COLLATE utf8mb4_general_ci NOT NULL,
  `role_name` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`role_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO roles VALUES ("a40f2a2a-9170-11ef-b929-0242ac130002", "admin");
INSERT INTO roles VALUES ("p40f3440-9170-11ef-b929-0242ac130002", "partner");
INSERT INTO roles VALUES ("cce0e790-9170-11ef-b929-0242ac130002", "customer");
INSERT INTO roles VALUES ("rfd1a802-19ed-4443-9275-79f43d812ce2", "restaurant");

CREATE TABLE `users` (
  `user_pk` char(36) COLLATE utf8mb4_general_ci NOT NULL,
  `user_name` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `user_last_name` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `user_email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `user_password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `user_role` char(36) COLLATE utf8mb4_general_ci NOT NULL,
  `user_created_at` int unsigned NOT NULL,
  `user_deleted_at` int unsigned NOT NULL,
  `user_blocked_at` int unsigned NOT NULL,
  `user_updated_at` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_pk`),
  UNIQUE KEY `user_email` (`user_email`),
  CONSTRAINT `fk_user_role` FOREIGN KEY (`user_role`) REFERENCES `roles` (`role_pk`) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO users VALUES ("0c3e60bd-13d0-4586-b75b-eee809c5a88c", "Aa", "Aaaa", "a@a.com", "scrypt:32768:8:1$uVSyaNKSvCVk2lMr$7e27abc754d0a059013ddc543ec0f3ecd0ba9d8c999a2e76d39bdf67893c94f313087bd1d750fc1b04a533edb253c6034ee232b3c4914705bb9defee0e126342", "cce0e790-9170-11ef-b929-0242ac130002", 0, 0, 0, 0);
INSERT INTO users VALUES ("1355a052-918d-11ef-b929-0242ac130002", "Bb", "Bbbb", "b@b.com", "scrypt:32768:8:1$uVSyaNKSvCVk2lMr$7e27abc754d0a059013ddc543ec0f3ecd0ba9d8c999a2e76d39bdf67893c94f313087bd1d750fc1b04a533edb253c6034ee232b3c4914705bb9defee0e126342", "cce0e790-9170-11ef-b929-0242ac130002", 0, 0, 0, 0);


CREATE TABLE `users_roles` (
  `user_role_user_fk` char(36) COLLATE utf8mb4_general_ci NOT NULL,
  `user_role_role_fk` char(36) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`user_role_user_fk`, `user_role_role_fk`),
  CONSTRAINT `fk_users_roles_user` FOREIGN KEY (`user_role_user_fk`) REFERENCES `users` (`user_pk`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  CONSTRAINT `fk_users_roles_role` FOREIGN KEY (`user_role_role_fk`) REFERENCES `roles` (`role_pk`)
  ON DELETE CASCADE
  ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO users_roles VALUES ("0c3e60bd-13d0-4586-b75b-eee809c5a88c", "cce0e790-9170-11ef-b929-0242ac130002");
INSERT INTO users_roles VALUES ("1355a052-918d-11ef-b929-0242ac130002", "cce0e790-9170-11ef-b929-0242ac130002");
