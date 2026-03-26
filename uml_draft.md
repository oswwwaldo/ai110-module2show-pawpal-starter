

### Owner
    Attributes
        name
        age
        availability_spots

        energy_level
        preferences

        zip_code
        work_mode
        commute_duration


    Methods
        work()
        chill()
        sleep()
        commute()



### Tasks
    Attributes
        task_name
        category
        min_duration
        duration
        location
        priority 
        starred
        status 
        'today'
        due_date
        remind_date
        frequency 
        note
        color
        is_weather_dependent

        is_mandatory
        energy_cost

    Methods
        create(taskName)
        edit(*)
        delete()

### Schedule
    Attributes
        hour
        day
        week
        month
        year

        total_free_time
        score_plan()

    Methods
        schedule(task)
        schedule(task, hour)
        forward()
        backward()

### Pets 

    Attributes 
        type
        breed
        name
        age
        weight
        health
        hunger
        hygiene 
        happiness
        energy
        thrist 
        activity_level

        last_fed_time
        last_bathed_time
        last_exercised_time
        last_drank_time
        last_played_time
        last_chilled_time
        last_roamed_time

        medication_frequency 

    Methods
        chill()
        roam()
        feed() 
        sleep()
        walk()
        play()
        massage()
        bathe()
