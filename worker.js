const json = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });
const cors = (response) => { response.headers.set('access-control-allow-origin','*'); response.headers.set('access-control-allow-headers','Content-Type, Authorization'); response.headers.set('access-control-allow-methods','GET,POST,DELETE,OPTIONS'); return response; };
const readJSON = async (request) => { try { return await request.json(); } catch { return {}; } };
const auth = (request, env) => {
  const value = request.headers.get('authorization') || '';
  if (!value.startsWith('Bearer ')) return false;
  return value.slice(7) === env.ADMIN_PASSWORD;
};
const protectedRoute = (request, env) => auth(request, env) ? null : cors(json({ error: 'Login required' }, 401));

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return cors(new Response(null, { status: 204 }));
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(request);

    try {
      if (url.pathname === '/api/health') return cors(json({ ok: true }));

      if (url.pathname === '/api/admin/login' && request.method === 'POST') {
        const body = await readJSON(request);
        if (body.username === 'admin' && env.ADMIN_PASSWORD && body.password === env.ADMIN_PASSWORD) {
          return cors(json({ access_token: env.ADMIN_PASSWORD }));
        }
        return cors(json({ error: 'Invalid credentials' }, 401));
      }

      if (url.pathname === '/api/profile' && request.method === 'GET') {
        const row = await env.DB.prepare('SELECT * FROM profile WHERE id=1').first();
        return cors(json(row || { id: 1, name: 'मनोज मिश्रा' }));
      }
      if (url.pathname === '/api/profile' && request.method === 'POST') {
        const denied = protectedRoute(request, env); if (denied) return denied;
        const b = await readJSON(request);
        await env.DB.prepare(`INSERT INTO profile (id,name,designation,district,bio_hi,bio_en,facebook,instagram,x,youtube,updated_at)
          VALUES (1,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
          ON CONFLICT(id) DO UPDATE SET name=excluded.name,designation=excluded.designation,district=excluded.district,bio_hi=excluded.bio_hi,bio_en=excluded.bio_en,facebook=excluded.facebook,instagram=excluded.instagram,x=excluded.x,youtube=excluded.youtube,updated_at=CURRENT_TIMESTAMP`)
          .bind(b.name||'',b.designation||'',b.district||'',b.bio_hi||'',b.bio_en||'',b.facebook||'',b.instagram||'',b.x||'',b.youtube||'').run();
        return cors(json({ ok: true }));
      }

      if (url.pathname === '/api/posts' && request.method === 'GET') {
        const r = await env.DB.prepare('SELECT * FROM posts WHERE published=1 ORDER BY id DESC').all();
        return cors(json(r.results));
      }
      if (url.pathname === '/api/posts' && request.method === 'POST') {
        const denied = protectedRoute(request, env); if (denied) return denied;
        const b = await readJSON(request);
        const r = await env.DB.prepare('INSERT INTO posts(title_hi,title_en,body_hi,body_en,type,published) VALUES(?,?,?,?,?,1) RETURNING *').bind(b.title_hi||'',b.title_en||'',b.body_hi||'',b.body_en||'',b.type||'News').first();
        return cors(json(r));
      }
      const postDelete = url.pathname.match(/^\/api\/posts\/(\d+)$/);
      if (postDelete && request.method === 'DELETE') { const denied = protectedRoute(request, env); if (denied) return denied; await env.DB.prepare('DELETE FROM posts WHERE id=?').bind(postDelete[1]).run(); return cors(json({ok:true})); }

      if (url.pathname === '/api/career' && request.method === 'GET') { const r = await env.DB.prepare('SELECT * FROM activities ORDER BY id DESC').all(); return cors(json(r.results)); }
      if (url.pathname === '/api/career' && request.method === 'POST') { const denied=protectedRoute(request,env); if(denied)return denied; const b=await readJSON(request); const r=await env.DB.prepare('INSERT INTO activities(year,title_hi,title_en,description_hi,description_en) VALUES(?,?,?,?,?) RETURNING *').bind(b.year||'',b.title_hi||'',b.title_en||'',b.description_hi||'',b.description_en||'').first(); return cors(json(r)); }
      const careerDelete=url.pathname.match(/^\/api\/career\/(\d+)$/); if(careerDelete&&request.method==='DELETE'){const denied=protectedRoute(request,env);if(denied)return denied;await env.DB.prepare('DELETE FROM activities WHERE id=?').bind(careerDelete[1]).run();return cors(json({ok:true}));}

      if (url.pathname === '/api/gallery' && request.method === 'GET') { const r=await env.DB.prepare('SELECT id,title,image_url AS image,category,created_at FROM gallery ORDER BY id DESC').all(); return cors(json(r.results)); }
      if (url.pathname === '/api/gallery' && request.method === 'POST') { const denied=protectedRoute(request,env);if(denied)return denied; const b=await readJSON(request); const r=await env.DB.prepare('INSERT INTO gallery(title,image_url,category) VALUES(?,?,?) RETURNING id,title,image_url AS image,category').bind(b.title||'',b.image_url||'',b.category||'').first(); return cors(json(r)); }
      const galleryDelete=url.pathname.match(/^\/api\/gallery\/(\d+)$/); if(galleryDelete&&request.method==='DELETE'){const denied=protectedRoute(request,env);if(denied)return denied;await env.DB.prepare('DELETE FROM gallery WHERE id=?').bind(galleryDelete[1]).run();return cors(json({ok:true}));}

      if (url.pathname === '/api/contact' && request.method === 'POST') { const b=await readJSON(request); await env.DB.prepare('INSERT INTO contact_messages(name,email,message) VALUES(?,?,?)').bind(b.name||'',b.email||'',b.message||'').run(); return cors(json({ok:true})); }
      if (url.pathname === '/api/contacts' && request.method === 'GET') { const denied=protectedRoute(request,env);if(denied)return denied; const r=await env.DB.prepare('SELECT * FROM contact_messages ORDER BY id DESC').all(); return cors(json(r.results)); }
      const contactDelete=url.pathname.match(/^\/api\/contacts\/(\d+)$/); if(contactDelete&&request.method==='DELETE'){const denied=protectedRoute(request,env);if(denied)return denied;await env.DB.prepare('DELETE FROM contact_messages WHERE id=?').bind(contactDelete[1]).run();return cors(json({ok:true}));}

      return cors(json({ error: 'Not found' }, 404));
    } catch (e) { return cors(json({ error: e.message || 'Server error' }, 500)); }
  }
};
