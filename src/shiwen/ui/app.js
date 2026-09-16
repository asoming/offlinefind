'use strict';
(() => {
const $ = id => document.getElementById(id);
const state = { language: 'zh', query: '', type: 'all', view: 'all', root: null,
  sort: 'relevance', items: [], selected: null, document: null, block: 0, hits: [],
  status: null, searchSequence: 0, previewSequence: 0, composing: false, busy: false };
const words = {
  zh: {
    allDocs:'全部文档',saved:'我的收藏',searchScope:'搜索范围',addFolder:'添加文件夹',
    manageFolders:'管理文件夹',settings:'设置',tagline:'记得内容，就找得到。',offline:'本地离线',
    searchPlaceholder:'搜索文档里的文字…',clearSearch:'清空搜索',all:'全部',titleAndBody:'搜索标题与正文',
    welcomeTitle:'让散落的文字，重新相遇。',welcomeBody:'选择存放文档的文件夹。拾文会在这台电脑上建立索引，帮你找回记得的那句话。',
    supported:'支持 PDF、Markdown、Word · 文件不会上传',sort:'排序',relevance:'相关度优先',recent:'最近修改',
    preview:'文档预览',save:'收藏文档',reveal:'在文件夹中显示',close:'关闭',chooseDocument:'选择一份文档，查看相关段落。',
    previous:'上一处命中',next:'下一处命中',openOriginal:'打开原文件',privacyFooter:'文件留在本机，内容只属于你',
    noAccount:'无账号 · 无上传 · 无遥测',language:'语言',appearance:'外观',system:'跟随系统',light:'浅色',dark:'深色',
    glass:'磨砂玻璃',resource:'后台资源',standard:'标准',low:'低占用',resourceNote:'后台串行解析文档。低占用模式会在任务之间留出更多间隔。',
    localData:'本地索引占用',indexPrivacy:'索引可能包含文档原文，未单独加密。请使用系统用户权限与磁盘加密保护这台设备。',
    clearData:'清除全部本地数据',folderNote:'只读取选定目录；跳过隐藏目录、依赖目录和符号链接。移除范围不会删除原文件。',
    indexState:'索引状态',retry:'重新检查与重试',statusNote:'扫描版 PDF 需要 OCR，当前版本仅检索可提取的文字。未能解析的文档仍可按文件名查找。',
    cancel:'取消',confirm:'确认',loadMore:'加载更多',ready:'文档已就绪',scanning:'正在发现文档',indexing:'正在建立索引',
    paused:'索引已暂停',error:'索引需要处理',idle:'文档已就绪',pause:'暂停索引',resume:'继续索引',
    found:'找到 {n} 份文档',atLeast:'已找到至少 {n} 份文档',folderCount:'{n} 个文件夹',processed:'已发现 {n} 份 · 已处理 {p} 份',
    noResults:'没有找到相关文档',noResultsHint:'试试其他关键词或搜索范围；有些文档可能还未完成索引。',
    savedEmpty:'还没有符合条件的收藏',nameOnly:'文件名匹配',savedToast:'已加入我的收藏',unsavedToast:'已取消收藏',
    page:'第 {n} 页',line:'第 {n} 行起',paragraph:'第 {n} 段',match:'命中位置 {n} / {total}',block:'内容 {n} / {total}',
    textPreview:'提取文本预览',noTextPreview:'这份文件暂无可预览的文字。可以用原应用打开，或在索引状态中查看原因。',
    removed:'已移除搜索范围，原文件保持不变',remove:'移除',exclude:'排除子目录',excluded:'已排除：',
    removeConfirm:'移除这个文件夹的索引与收藏引用？原文件不会被删除。',excludePrompt:'输入相对于该文件夹的子目录路径，例如 archive/private。',
    clearConfirm:'这将清除索引、收藏、文件夹范围与设置。原始文档不会被修改或删除。',cleared:'本地数据已清除',
    retrying:'已安排重新检查',noFolders:'尚未添加文件夹',connectionError:'无法连接本地检索服务，请重启应用。',
    unavailable:'文件或目录当前不可用',partial:'部分页面无可提取文字',no_text:'未提取到文字，可能需要 OCR',
    encrypted:'文件受密码保护',file_limit:'超过 100 MiB 文件上限',text_limit:'超过文本提取上限',page_limit:'超过 1,000 页上限',
    timeout:'解析超时',parse_error:'未能解析文件',encoding:'请将文本另存为 UTF-8',permission:'没有读取权限',
    cloud:'文件尚未下载到本机',pending:'内容待更新',storage_error:'本地存储异常，请检查磁盘空间',
    query_too_short:'每个搜索词至少需要 2 个字符',query_too_long:'搜索内容不能超过 256 个字符',
    too_many_terms:'最多组合 12 个搜索词',unclosed_quote:'请补全短语的双引号',invalid_folder:'文件夹无效或不可访问',
    folder_too_broad:'请选择具体的文档目录，不要选择整盘或包含拾文数据的目录',invalid_exclusion:'请输入当前范围内的有效子目录',
    invalid_setting:'设置值无效',operation_failed:'操作未完成，请检查文件与权限后重试',desktop_only:'请在桌面应用中使用系统文件夹选择器；开发预览可通过 --folder 添加目录',
    loading:'正在搜索…',disconnected:'目录不可用',partialList:'仅显示前 50 条，可继续加载',
  },
  en: {
    allDocs:'All documents',saved:'Bookmarks',searchScope:'SEARCH FOLDERS',addFolder:'Add folder',manageFolders:'Manage folders',
    settings:'Settings',tagline:'Remember the words. Find the file.',offline:'Offline',searchPlaceholder:'Search inside your documents…',
    clearSearch:'Clear search',all:'All',titleAndBody:'Search names and contents',welcomeTitle:'Your words, within reach.',
    welcomeBody:'Choose a folder of documents. Shiwen builds an index on this computer, so a remembered phrase leads you back to the right file.',
    supported:'PDF, Markdown and Word · Nothing uploaded',sort:'Sort results',relevance:'Most relevant',recent:'Last modified',
    preview:'Document preview',save:'Bookmark document',reveal:'Show in folder',close:'Close',chooseDocument:'Select a document to read the matching passage.',
    previous:'Previous match',next:'Next match',openOriginal:'Open original',privacyFooter:'Your files stay here. Your words stay yours.',
    noAccount:'No account · No uploads · No telemetry',language:'Language',appearance:'Appearance',system:'System',light:'Light',dark:'Dark',
    glass:'Frosted glass',resource:'Background usage',standard:'Standard',low:'Low',resourceNote:'Documents are parsed one at a time. Low mode adds a pause between tasks.',
    localData:'Local index size',indexPrivacy:'The index may contain original document text and is not separately encrypted. Protect it with your OS account and disk encryption.',
    clearData:'Clear all local data',folderNote:'Only selected folders are read. Hidden folders, dependencies and symlinks are skipped. Removing a scope never deletes original files.',
    indexState:'Index status',retry:'Recheck and retry',statusNote:'Scanned PDFs need OCR, which is not included in this version. Documents without extractable text can still be found by name.',
    cancel:'Cancel',confirm:'Confirm',loadMore:'Load more',ready:'Documents are ready',scanning:'Discovering documents',indexing:'Indexing documents',
    paused:'Indexing paused',error:'Index needs attention',idle:'Documents are ready',pause:'Pause indexing',resume:'Resume indexing',
    found:'{n} documents found',atLeast:'At least {n} documents found',folderCount:'{n} folders',processed:'{n} discovered · {p} processed',
    noResults:'No matching documents',noResultsHint:'Try another phrase or folder. Some documents may still be waiting to be indexed.',
    savedEmpty:'No matching bookmarks yet',nameOnly:'Name match',savedToast:'Bookmark added',unsavedToast:'Bookmark removed',
    page:'Page {n}',line:'From line {n}',paragraph:'Paragraph {n}',match:'Match location {n} of {total}',block:'Content {n} of {total}',
    textPreview:'Extracted text preview',noTextPreview:'There is no text to preview. Open the original file, or check its indexing status.',
    removed:'Search scope removed. Original files are unchanged.',remove:'Remove',exclude:'Exclude subfolder',excluded:'Excluded: ',
    removeConfirm:'Remove this folder’s index and bookmark references? Original files will not be deleted.',
    excludePrompt:'Enter a subfolder path relative to this folder, for example archive/private.',
    clearConfirm:'This removes the index, bookmarks, folder scopes and settings. Original documents will not be changed or deleted.',
    cleared:'Local data cleared',retrying:'Recheck scheduled',noFolders:'No folders added',connectionError:'Cannot connect to the local search service. Please restart Shiwen.',
    unavailable:'File or folder is unavailable',partial:'Some pages have no extractable text',no_text:'No text extracted; OCR may be needed',
    encrypted:'Password-protected file',file_limit:'File exceeds 100 MiB',text_limit:'Extracted text exceeds the limit',page_limit:'PDF exceeds 1,000 pages',
    timeout:'Parsing timed out',parse_error:'Could not parse this file',encoding:'Please save this text file as UTF-8',permission:'Read permission denied',
    cloud:'File has not been downloaded',pending:'Content update pending',storage_error:'Local storage error; check available disk space',
    query_too_short:'Each search term needs at least 2 characters',query_too_long:'Search text is limited to 256 characters',too_many_terms:'Use up to 12 search terms',
    unclosed_quote:'Close the quotation marks around your phrase',invalid_folder:'Folder is invalid or unavailable',
    folder_too_broad:'Choose a document folder, not an entire drive or a parent of Shiwen’s data directory',invalid_exclusion:'Enter a valid subfolder within this scope',
    invalid_setting:'Invalid setting',operation_failed:'Could not complete the operation. Check the file and permissions, then retry.',
    desktop_only:'Use the folder picker in the desktop app. In developer preview, add folders with --folder.',loading:'Searching…',
    disconnected:'Folder unavailable',partialList:'First 50 results; load more to continue',
  }
};
function t(key, values = {}) { let text = words[state.language][key] || words.en[key] || key;
  for (const [name, value] of Object.entries(values)) text = text.replaceAll(`{${name}}`, String(value)); return text; }
const paths = {
  book:'M12 5v15M3 4h4c2 0 4 1 5 2 1-1 3-2 5-2h4v15h-4c-2 0-4 1-5 2-1-1-3-2-5-2H3z',
  files:'M8 3h8l4 4v13H8zM16 3v5h4M4 7v14',bookmark:'M6 3h12v18l-6-4-6 4z',
  folder:'M3 6h7l2 2h9v12H3zM3 6V4h7l2 2h7v2',plus:'M12 5v14M5 12h14',
  search:'M20 20l-5-5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',x:'M6 6l12 12M6 18 18 6',
  shield:'M12 3l8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6',
  lock:'M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5zM12 14v3',
  text:'M4 5h16M4 10h10M4 15h16M4 20h10',chevron:'M9 5l7 7-7 7',
  up:'M6 15l6-6 6 6',down:'M6 9l6 6 6-6',external:'M13 4h7v7M20 4l-10 10M10 4H4v16h16v-6',
  settings:'M4 7h16M4 17h16M8 4v6M16 14v6'
};
function icon(name) { const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('class','icon'); svg.setAttribute('aria-hidden','true');
  const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',paths[name]||paths.files);svg.append(path);return svg; }
function make(tag, cls, text) { const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node; }
function highlight(node, text, spans = []) { const chars=Array.from(text);node.replaceChildren();let previous=0;
  for(const [a,b] of spans){node.append(document.createTextNode(chars.slice(previous,a).join('')));node.append(make('mark','',chars.slice(a,b).join('')));previous=b;}
  node.append(document.createTextNode(chars.slice(previous).join(''))); }
function size(bytes) { if(bytes<1024)return `${bytes} B`;if(bytes<1048576)return `${(bytes/1024).toFixed(0)} KiB`;return `${(bytes/1048576).toFixed(1)} MiB`; }
function basename(path) { return path.split(/[\\/]/).filter(Boolean).pop() || path; }
function toast(message) { $('toast').textContent=message;$('toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').hidden=true,4500); }
async function api(method,args={}) { let result;
  if(window.pywebview?.api)result=await window.pywebview.api.call(method,args);
  else if(window.SHIWEN_BOOT.token){const response=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json','X-Shiwen-Token':window.SHIWEN_BOOT.token},body:JSON.stringify({method,args})});if(!response.ok)throw new Error('connectionError');result=await response.json();}
  else throw new Error('connectionError');
  if(!result.ok)throw new Error(result.error);return result.data;
}
function run(action) { return Promise.resolve().then(action).catch(error=>toast(t(error.message))); }
function translate() {
  document.documentElement.lang=state.language==='zh'?'zh-CN':'en';
  document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));
  document.querySelectorAll('[data-placeholder]').forEach(el=>el.placeholder=t(el.dataset.placeholder));
  document.querySelectorAll('[data-title]').forEach(el=>{el.title=t(el.dataset.title);el.setAttribute('aria-label',el.title);});
  document.querySelectorAll('[data-label]').forEach(el=>el.setAttribute('aria-label',t(el.dataset.label)));
}
function applySettings(settings) { state.language=settings.language;translate();
  const dark=settings.theme==='dark'||(settings.theme==='system'&&matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme=dark?'dark':'light';document.body.classList.toggle('solid',!settings.glass);
  for(const name of ['language','theme','resource'])$(name).value=settings[name];$('glass').checked=settings.glass;
}
function drawFolders() { $('folders').replaceChildren();$('folder-management').replaceChildren();
  for(const root of state.status.roots){
    const button=make('button',`folder-item${state.root===root.id?' active':''}`);button.append(icon('folder'),make('span','folder-name',basename(root.path)));button.title=root.path;
    button.setAttribute('aria-pressed',String(state.root===root.id));button.onclick=()=>{state.root=state.root===root.id?null:root.id;state.view='all';updateNavigation();drawFolders();run(()=>search());};$('folders').append(button);
    const panel=make('div','managed-folder');panel.append(make('strong','',basename(root.path)),make('p','',root.path));
    if(!root.available)panel.append(make('p','',t('disconnected')));
    if(root.excluded.length)panel.append(make('div','exclusion-list',t('excluded')+root.excluded.join(', ')));
    const actions=make('div','folder-actions'),exclude=make('button','secondary',t('exclude')),remove=make('button','danger',t('remove'));
    exclude.onclick=()=>run(async()=>{const answer=await confirm(t('exclude'),t('excludePrompt'),'');if(answer===null)return;await api('exclude',{root_id:root.id,relative:answer});await refreshStatus();await search();});
    remove.onclick=()=>run(async()=>{if(await confirm(t('remove'),t('removeConfirm'))===null)return;await api('remove_root',{root_id:root.id});if(state.root===root.id)state.root=null;state.selected=null;await refreshStatus();await search();toast(t('removed'));});
    actions.append(exclude,remove);panel.append(actions);$('folder-management').append(panel);
  }
}
function updateNavigation(){document.querySelectorAll('[data-view]').forEach(b=>{const active=b.dataset.view===state.view&&!state.root;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  document.querySelectorAll('[data-type]').forEach(b=>{const active=b.dataset.type===state.type;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});}
async function refreshStatus(){const status=await api('status');const previous=state.status;state.status=status;applySettings(status.settings);
  $('all-count').textContent=status.counts.total;$('saved-count').textContent=status.counts.saved;
  const phase=status.paused?'paused':status.progress.phase;$('status-label').textContent=t(phase);
  $('index-detail').textContent=t('folderCount',{n:status.roots.length});
  const processing=t('processed',{n:status.progress.discovered,p:status.progress.processed});$('index-progress').textContent=status.progress.error?t(status.progress.error):processing;
  $('pause').textContent=t(status.paused?'resume':'pause');$('disk-size').textContent=size(status.disk_bytes);$('data-directory').textContent=status.data_directory;
  $('status-counts').replaceChildren();for(const [name,n]of Object.entries(status.counts.by_status)){const row=make('div','status-row');row.append(make('span','',t(name)),make('span','',n));$('status-counts').append(row);}
  $('welcome').hidden=Boolean(status.roots.length);$('workspace').hidden=!status.roots.length;
  if(JSON.stringify(previous?.roots)!==JSON.stringify(status.roots)||previous?.settings.language!==status.settings.language)drawFolders();
  return !previous||JSON.stringify(previous.counts)!==JSON.stringify(status.counts)||previous.progress.processed!==status.progress.processed;
}
async function search(append=false) { const sequence=++state.searchSequence;const offset=append?state.items.length:0;
  $('result-summary').textContent=t('loading');try{const result=await api('search',{query:state.query,file_type:state.type,root_id:state.root,saved:state.view==='saved',sort:state.sort,offset});
  if(sequence!==state.searchSequence)return;state.items=append?state.items.concat(result.items):result.items;
  $('result-summary').textContent=t(result.has_more?'atLeast':'found',{n:state.items.length});$('load-more').hidden=!result.has_more;drawResults();
  if(!state.items.some(item=>item.id===state.selected)){state.selected=state.items[0]?.id??null;await select(state.selected,false);}else await select(state.selected,false);
  }catch(error){if(sequence!==state.searchSequence)return;$('result-summary').textContent=t(error.message);state.items=[];drawResults(t(error.message));await select(null,false);}
}
function drawResults(message){$('results').replaceChildren();if(!state.items.length){const empty=make('div','empty');empty.append(icon('search'),make('div','',message||t(state.view==='saved'?'savedEmpty':'noResults')),make('p','',t('noResultsHint')));$('results').append(empty);return;}
  for(const item of state.items){const button=make('button',`result${item.id===state.selected?' active':''}`);button.dataset.id=item.id;button.setAttribute('aria-pressed',String(item.id===state.selected));
    const head=make('span','result-head'),file=make('span',`file-icon ${item.type}`,item.type==='docx'?'DOC':item.type.toUpperCase()),labels=make('span'),title=make('span','result-title');highlight(title,item.name,item.title_ranges);
    const date=new Date(item.mtime_ns/1e6).toLocaleDateString(state.language==='zh'?'zh-CN':'en-US',{month:'short',day:'numeric'});
    labels.append(title,make('span','result-meta',`${date} · ${size(item.size)}${item.saved?' · '+t('saved'):''}`));head.append(file,labels);button.append(head);
    for(const excerpt of item.excerpts){const span=make('span','excerpt');highlight(span,excerpt.text,excerpt.ranges);if(excerpt.before)span.prepend(document.createTextNode('…'));if(excerpt.after)span.append(document.createTextNode('…'));button.append(span);}
    const parent=item.path.replace(/[\\/][^\\/]+$/,'');const path=make('span','result-path');path.append(icon('folder'),document.createTextNode(basename(parent)));button.append(path);
    if(item.status!=='ready')button.append(make('span','result-warning',t(item.status)));else if(item.name_only)button.append(make('span','result-warning',t('nameOnly')));
    button.onclick=()=>run(()=>select(item.id,true));button.ondblclick=()=>run(()=>api('open',{document_id:item.id}));
    button.onkeydown=event=>{if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();const index=state.items.findIndex(i=>i.id===item.id);const next=state.items[index+(event.key==='ArrowDown'?1:-1)];if(next){run(()=>select(next.id,false));$('results').querySelector(`[data-id="${next.id}"]`)?.focus();}}else if(event.key==='Enter'){event.preventDefault();run(()=>api('open',{document_id:item.id}));}};
    $('results').append(button);
  }
}
async function select(id,show=true) { state.selected=id;const sequence=++state.previewSequence;
  $('results').querySelectorAll('.result').forEach(el=>{const active=Number(el.dataset.id)===id;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});
  for(const name of ['bookmark','reveal'])$(name).disabled=!id;
  if(!id){state.document=null;$('preview-empty').hidden=false;$('document').hidden=true;return;}
  const document=await api('document',{document_id:id,query:state.query});if(sequence!==state.previewSequence)return;
  state.document=document;state.hits=document.blocks.map((b,i)=>b.ranges.length?i:-1).filter(i=>i>=0);state.block=state.hits[0]??0;
  $('preview-empty').hidden=true;$('document').hidden=false;$('bookmark').setAttribute('aria-pressed',String(Boolean(document.saved)));
  $('paper-title').textContent=document.name.replace(/\.[^.]+$/,'');$('paper-type').textContent=`${document.type.toUpperCase()} / ${t('textPreview')}`;
  $('document-path').textContent=document.path;$('document-status').textContent=document.status==='ready'?'':t(document.status);drawBlock();if(show)$('workspace').classList.add('show-preview');
}
function drawBlock(){const doc=state.document;if(!doc)return;const block=doc.blocks[state.block];const indices=state.hits.length?state.hits:doc.blocks.map((_,i)=>i);const position=indices.indexOf(state.block);
  $('match-label').textContent=t(state.hits.length?'match':'block',{n:indices.length?position+1:0,total:indices.length});$('prev-hit').disabled=position<=0;$('next-hit').disabled=position>=indices.length-1;
  $('paper-location').textContent=block?t(block.kind,{n:block.location}):'';$('paper-number').textContent=block?.location??'';
  if(block)highlight($('paper-text'),block.text,block.ranges);else $('paper-text').textContent=t('noTextPreview');
}
function moveHit(step){if(!state.document)return;const indices=state.hits.length?state.hits:state.document.blocks.map((_,i)=>i);const next=indices[indices.indexOf(state.block)+step];if(next!==undefined){state.block=next;drawBlock();}}
function confirm(title,text,value=null){$('confirm-title').textContent=title;$('confirm-text').textContent=text;$('confirm-input').hidden=value===null;$('confirm-input').value=value??'';$('confirm-dialog').showModal();return new Promise(resolve=>{let done=false;
  const finish=answer=>{if(done)return;done=true;$('confirm-dialog').close();resolve(answer);};$('confirm-ok').onclick=()=>finish(value===null?true:$('confirm-input').value);$('confirm-cancel').onclick=()=>finish(null);$('confirm-dialog').oncancel=()=>finish(null);
});}
async function addFolder(){const id=await api('choose_folder');if(id!==null){await refreshStatus();await search();}}
document.querySelectorAll('[data-icon]').forEach(el=>{if(el.className)el.append(icon(el.dataset.icon));else el.replaceWith(icon(el.dataset.icon));});
// Icons replacing decorative spans preserve the semantic wrappers and labels.
document.querySelectorAll('[data-close]').forEach(button=>button.onclick=()=>$(button.dataset.close).close());
for(const id of ['add-small','add-first','add-managed'])$(id).onclick=()=>run(addFolder);
document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>{state.view=button.dataset.view;state.root=null;updateNavigation();drawFolders();run(()=>search());});
document.querySelectorAll('[data-type]').forEach(button=>button.onclick=()=>{state.type=button.dataset.type;updateNavigation();run(()=>search());});
$('manage-folders').onclick=()=>{$('folders-dialog').showModal();drawFolders();};$('settings-button').onclick=()=>$('settings-dialog').showModal();$('index-status').onclick=()=>$('status-dialog').showModal();
$('search-form').onsubmit=event=>{event.preventDefault();clearTimeout(search.timer);state.query=$('query').value;run(()=>search());};
function schedule(){if(state.composing)return;clearTimeout(search.timer);search.timer=setTimeout(()=>{state.query=$('query').value;run(()=>search());},180);}
$('query').oninput=schedule;$('query').oncompositionstart=()=>{state.composing=true;clearTimeout(search.timer);};$('query').oncompositionend=()=>{state.composing=false;schedule();};
$('clear-query').onclick=()=>{clearTimeout(search.timer);$('query').value='';state.query='';run(()=>search());$('query').focus();};
$('sort').onchange=()=>{state.sort=$('sort').value;run(()=>search());};$('load-more').onclick=()=>run(()=>search(true));
$('bookmark').onclick=()=>run(async()=>{const saved=!state.document.saved;await api('bookmark',{document_id:state.selected,saved});await refreshStatus();await search();toast(t(saved?'savedToast':'unsavedToast'));});
$('open-document').onclick=()=>run(()=>api('open',{document_id:state.selected}));$('reveal').onclick=()=>run(()=>api('open',{document_id:state.selected,reveal:true}));
$('prev-hit').onclick=()=>moveHit(-1);$('next-hit').onclick=()=>moveHit(1);$('close-preview').onclick=()=>$('workspace').classList.remove('show-preview');
$('pause').onclick=()=>run(async()=>{await api('pause',{paused:!state.status.paused});await refreshStatus();});$('retry').onclick=()=>run(async()=>{await api('retry');toast(t('retrying'));});
for(const key of ['theme','language','glass','resource'])$(key).onchange=()=>run(async()=>{await api('setting',{key,value:key==='glass'?$(key).checked:$(key).value});await refreshStatus();drawFolders();await search();});
$('clear-data').onclick=()=>run(async()=>{if(await confirm(t('clearData'),t('clearConfirm'))===null)return;await api('clear');state.selected=null;state.root=null;state.query='';state.type='all';state.view='all';$('query').value='';updateNavigation();$('settings-dialog').close();await refreshStatus();await search();toast(t('cleared'));});
document.addEventListener('keydown',event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();$('query').focus();$('query').select();}});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{if(state.status)applySettings(state.status.settings);});
$('version').textContent=window.SHIWEN_BOOT.version;if(/Mac/.test(navigator.platform))$('search-key').textContent='⌘ K';
let started=false;async function start(){if(started)return;started=true;try{await refreshStatus();await search();$('query').focus();setInterval(()=>{if(state.busy)return;state.busy=true;refreshStatus().then(changed=>{if(changed&&!state.composing)return search();}).catch(()=>{}).finally(()=>state.busy=false);},2200);}catch(error){toast(t(error.message));}}
translate();updateNavigation();window.addEventListener('pywebviewready',start);if(window.SHIWEN_BOOT.token)start();
})();
