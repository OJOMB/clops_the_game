def display_level_one_intro(pilot):
    intro = True
    warp = Warp()
    all_sprites.add(warp)
    player = Player(pilot)
    all_sprites.add(player)
    tfs_mothership = TFSMothership()
    all_sprites.add(tfs_mothership)
    TFSship_enter = True
    Dialogue = False
    TFSship_leaves = False
    asteroids = False
    finished = False
    while intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        if tfs_mothership.rect.x == width/2:
            dialogue = True
        while dialogue:
            dialogue_one = True
            while dialogue_one:
                for event in pg.event.get():
                    if event.type == KEYUP:
                        if event.key == K_RETURN:
                            dialogue_one = False
                            dialogue_two = True
                screen.blit(frame, (0,height - 230))
                screen.blit(TFS_house_img, (60, height - 230 + 40))
                draw_text(screen, "Clops stormed off a few days ago...", 
                        "PXFXshadow-3.ttf", 50, width/2, height - 115, colour=black)
            while dialogue_two:
                for event in pg.event.get():
                    if event.type == pg.KEYUP:
                        if event.key == K_RETURN:
                            dialogue_two = False
                            dialogue_three = True
                screen.blit(frame, (0,height - 230))
                screen.blit(TFS_house_img, (60, height - 230 + 40))
                draw_text(screen, "We think he's using drones to control", 
                        "PXFXshadow-3.ttf", 50, width/2, height - 115, colour=black)
                draw_text(screen, "a bunch of spaceships in the Sheffield galactic quadrant", 
                        "PXFXshadow-3.ttf", 50, width/2, height - 115 + 55, colour=black)
        if asteroids:
            draw_text(screen, "LEVEL ONE", "PXFXshadow-3.ttf", 75, width/2, height/2)
            for i in range(20):
                meteor = Meteor(5,2)
                all_sprites.add(meteor)
                meteors.add(meteor)
        for meteor in meteors:
            if meteor.rect.y > height/2 -200:
                meteor.kill()
                explosion = MeteorExplosion(meteor)
                all_sprites.add(explosion)
        #CHECKS WHETHER BULLET HITS METEOR SPRITE
        hits = pg.sprite.groupcollide(meteors, bullets, True, True)
        if hits:
            for key in hits.keys():
                explosion = MeteorExplosion(key)
                all_sprites.add(explosion)
                explosions.add(explosion)
        screen.fill(black)
        screen.blit(stars,(0,0))
        all_sprites.update()
        all_sprites.draw(screen)
        pg.display.flip()
        if not meteors and finished:
            return player

