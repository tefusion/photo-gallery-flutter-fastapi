DELIMITER //

CREATE DATABASE images;
USE images;

CREATE TABLE `image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(20),
  `description` varchar(100),
  `file_path` varchar(100) NOT NULL,
  `time_created` datetime,
  PRIMARY KEY (`id`)
);

CREATE TABLE `tag` (
  `tag_id` int(11) NOT NULL AUTO_INCREMENT,
  `tname` varchar(20) NOT NULL,
  PRIMARY KEY (`tag_id`)
);

CREATE TABLE `tagmap` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  `pos` int(11) NOT NULL,
  PRIMARY KEY (`id`)
);



CREATE PROCEDURE dragInFrontOfOtherImage(
IN idShip INT,
IN idDestination INT,
IN tagname VARCHAR(100)
)
BEGIN

SET @posShip=0;
SET @posDestination=0;
Set @tagId=0;


SELECT @tagId:=t.tag_id FROM tag t WHERE t.tname=tagname;
SELECT @posShip:=tm.pos FROM tagmap tm WHERE tm.tag_id=@tagId AND tm.image_id=idShip;
SELECT @posDestination:=tm.pos FROM tagmap tm WHERE tm.tag_id=@tagId AND tm.image_id=idDestination;

    IF @posShip < @posDestination #if image in front of destination image
    THEN 
		UPDATE tagmap #make space by moving images in between up
		SET pos=pos-1 
		WHERE id>0 AND tag_id=@tagId AND pos>@posShip AND pos<@posDestination;
        
        UPDATE tagmap
		SET pos=(@posDestination-1)
		WHERE id>0 AND tag_id=@tagId AND image_id=idShip;


    ELSEIF @posShip > @posDestination #if image behind destination image
    THEN
         UPDATE tagmap #make space by moving images in between down
		SET pos=pos+1
		WHERE id>0 AND tag_id=@tagId AND pos>=@posDestination AND pos<@posShip;
        
        UPDATE tagmap
		SET pos=@posDestination
		WHERE id>0 AND tag_id=@tagId AND image_id=idShip;
    END IF;

    



 END//
 
 DELIMITER ;