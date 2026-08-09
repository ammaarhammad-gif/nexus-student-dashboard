import sys
from database import init_db, get_connection
from models import (
    get_user_profile, get_all_subjects, get_subject_hierarchy,
    get_all_subjects_with_stats, global_nexus_search,
    get_daily_plans, get_all_goals, get_all_terms,
    get_user_wallpaper_config, get_user_theme
)

print('1. Initializing DB & migrations...')
init_db()
print('   [OK] DB initialized.')

print('2. Testing user fetching...')
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('SELECT id, username FROM users LIMIT 1;')
        u = cur.fetchone()

if u:
    user_id = u[0]
    username = u[1]
    print(f'   [OK] Found test user: id={user_id}, username={username}')
    
    print('3. Testing profile & theme...')
    prof = get_user_profile(user_id)
    th = get_user_theme(user_id)
    wp = get_user_wallpaper_config(user_id)
    print(f"   [OK] Profile={prof.get('name')}, Theme={th}, WP_Mode={wp.get('mode')}")
    
    print('4. Testing syllabus hierarchy & statistics...')
    subs = get_all_subjects(user_id)
    stats = get_all_subjects_with_stats(user_id)
    print(f'   [OK] Subjects count={len(subs)}, Stats count={len(stats)}')
    if subs:
        hier = get_subject_hierarchy(user_id, subs[0]['id'])
        print(f"   [OK] Subject {subs[0]['name']} has {len(hier)} chapters")
        
    print('5. Testing planner & goals...')
    plans = get_daily_plans(user_id, '2026-08-09')
    goals = get_all_goals(user_id)
    terms = get_all_terms(user_id)
    print(f'   [OK] Daily plans={len(plans)}, Goals={len(goals)}, Terms={len(terms)}')
    
    print('6. Testing Global Nexus Search...')
    res = global_nexus_search(user_id, 'Math')
    print(f'   [OK] Search hits for Math = {sum(len(v) for v in res.values())}')
    res2 = global_nexus_search(user_id, 'Force')
    print(f'   [OK] Search hits for Force = {sum(len(v) for v in res2.values())}')
    
    print('\n[ALL TESTS PASSED SUCCESSFULLY]')
else:
    print('   No users found in database, skipped user queries.')
