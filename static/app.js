/*
QiitaClientApp

This implementation: 2026
License: MIT
*/

(function () {
  "use strict";

  const state = {
    articles: { page: 1, perPage: 20, query: "", tag: "" },
    stockedIds: new Set(),
    currentArticle: null,
    currentDraftId: null,
  };

  const els = {};

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    cacheElements();
    bindEvents();
    showView("articles");
    loadArticles();
  }

  function cacheElements() {
    els.errorBanner = document.getElementById("error-banner");
    els.tabButtons = document.querySelectorAll(".tab-button");
    els.views = document.querySelectorAll(".view");

    els.articlesForm = document.getElementById("articles-search-form");
    els.articlesQuery = document.getElementById("articles-query");
    els.articlesTag = document.getElementById("articles-tag");
    els.articlesList = document.getElementById("articles-list");
    els.articlesPrev = document.getElementById("articles-prev");
    els.articlesNext = document.getElementById("articles-next");
    els.articlesPageLabel = document.getElementById("articles-page-label");

    els.articleDetailContent = document.getElementById("article-detail-content");

    els.stocksList = document.getElementById("stocks-list");

    els.draftsList = document.getElementById("drafts-list");
    els.draftNewButton = document.getElementById("draft-new-button");

    els.draftEditorForm = document.getElementById("draft-editor-form");
    els.draftId = document.getElementById("draft-id");
    els.draftTitle = document.getElementById("draft-title");
    els.draftTags = document.getElementById("draft-tags");
    els.draftPrivate = document.getElementById("draft-private");
    els.draftBody = document.getElementById("draft-body");
    els.draftPreview = document.getElementById("draft-preview");
    els.draftStatusInfo = document.getElementById("draft-status-info");
    els.draftPublishButton = document.getElementById("draft-publish-button");
    els.draftSyncButton = document.getElementById("draft-sync-button");
    els.draftDeleteButton = document.getElementById("draft-delete-button");
  }

  function bindEvents() {
    els.tabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const view = button.dataset.view;
        showView(view);
        if (view === "articles") loadArticles();
        if (view === "stocks") loadStocks();
        if (view === "drafts") loadDrafts();
      });
    });

    document.querySelectorAll(".back-button").forEach((button) => {
      button.addEventListener("click", () => {
        const target = button.dataset.back;
        showView(target);
        if (target === "articles") loadArticles();
        if (target === "drafts") loadDrafts();
      });
    });

    els.articlesForm.addEventListener("submit", (event) => {
      event.preventDefault();
      state.articles.page = 1;
      state.articles.query = els.articlesQuery.value.trim();
      state.articles.tag = els.articlesTag.value.trim();
      loadArticles();
    });

    els.articlesPrev.addEventListener("click", () => {
      if (state.articles.page > 1) {
        state.articles.page -= 1;
        loadArticles();
      }
    });

    els.articlesNext.addEventListener("click", () => {
      state.articles.page += 1;
      loadArticles();
    });

    els.draftNewButton.addEventListener("click", () => openDraftEditor(null));

    els.draftBody.addEventListener("input", renderDraftPreview);

    els.draftEditorForm.addEventListener("submit", onSaveDraft);
    els.draftPublishButton.addEventListener("click", onPublishDraft);
    els.draftSyncButton.addEventListener("click", onSyncDraft);
    els.draftDeleteButton.addEventListener("click", onDeleteDraft);
  }

  function showView(name) {
    els.views.forEach((view) => {
      view.classList.toggle("active", view.id === `view-${name}`);
    });
    els.tabButtons.forEach((button) => {
      button.classList.toggle("active", button.dataset.view === name);
    });
    clearError();
  }

  function showError(message) {
    els.errorBanner.textContent = message;
    els.errorBanner.hidden = false;
  }

  function clearError() {
    els.errorBanner.hidden = true;
    els.errorBanner.textContent = "";
  }

  async function apiRequest(path, options) {
    let response;
    try {
      response = await fetch(path, options);
    } catch (networkError) {
      throw new Error("サーバーへ接続できませんでした。起動状態をご確認くだされ。");
    }
    if (!response.ok) {
      let detail = `リクエストに失敗いたし候（status=${response.status}）`;
      try {
        const body = await response.json();
        if (body && body.detail) detail = body.detail;
      } catch (_ignored) {
        // レスポンスボディがJSONでない場合はデフォルトメッセージを使う
      }
      throw new Error(detail);
    }
    if (response.status === 204) return null;
    return response.json();
  }

  // ---- 記事一覧・詳細 ----

  async function loadArticles() {
    clearError();
    els.articlesPageLabel.textContent = `${state.articles.page}ページ目`;
    const params = new URLSearchParams({
      page: String(state.articles.page),
      per_page: String(state.articles.perPage),
    });
    if (state.articles.query) params.set("query", state.articles.query);
    if (state.articles.tag) params.set("tag", state.articles.tag);

    try {
      const items = await apiRequest(`/api/articles?${params.toString()}`);
      renderArticlesList(items);
    } catch (error) {
      showError(error.message);
    }
  }

  function renderArticlesList(items) {
    els.articlesList.innerHTML = "";
    if (!items || items.length === 0) {
      els.articlesList.innerHTML = "<li class=\"item-card\">記事が見つかりませんでした</li>";
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "item-card";

      const main = document.createElement("div");
      main.className = "item-card-main";
      main.innerHTML = `
        <p class="item-card-title"></p>
        <p class="item-card-meta"></p>
      `;
      main.querySelector(".item-card-title").textContent = item.title || "(無題)";
      main.querySelector(".item-card-meta").textContent =
        `@${item.user ? item.user.id : "unknown"} / LGTM ${item.likes_count ?? 0}`;
      main.addEventListener("click", () => openArticleDetail(item.id));

      li.appendChild(main);
      els.articlesList.appendChild(li);
    });
  }

  async function openArticleDetail(itemId) {
    clearError();
    showView("article-detail");
    els.articleDetailContent.innerHTML = "<p>読み込み中...</p>";
    try {
      const item = await apiRequest(`/api/articles/${itemId}`);
      state.currentArticle = item;
      renderArticleDetail(item);
    } catch (error) {
      els.articleDetailContent.innerHTML = "";
      showError(error.message);
    }
  }

  function renderArticleDetail(item) {
    const tags = (item.tags || []).map((t) => `<span class="tag-badge">${escapeHtml(t.name)}</span>`).join("");
    const bodyHtml = renderMarkdown(item.body);
    els.articleDetailContent.innerHTML = `
      <h2>${escapeHtml(item.title || "")}</h2>
      <p class="item-card-meta">@${escapeHtml(item.user ? item.user.id : "unknown")}</p>
      <div>${tags}</div>
      <p><button id="stock-toggle-button"></button></p>
      <div class="markdown-body">${bodyHtml}</div>
    `;
    const stockButton = document.getElementById("stock-toggle-button");
    updateStockButtonLabel(stockButton, state.stockedIds.has(item.id));
    stockButton.addEventListener("click", () => toggleStock(item.id, stockButton));
  }

  function renderMarkdown(markdown) {
    const rawHtml = window.marked ? window.marked.parse(markdown || "") : escapeHtml(markdown || "");
    return window.DOMPurify ? window.DOMPurify.sanitize(rawHtml) : escapeHtml(markdown || "");
  }

  function updateStockButtonLabel(button, stocked) {
    button.textContent = stocked ? "ストック解除する" : "ストックする";
  }

  async function toggleStock(itemId, button) {
    clearError();
    const alreadyStocked = state.stockedIds.has(itemId);
    try {
      if (alreadyStocked) {
        await apiRequest(`/api/stocks/${itemId}`, { method: "DELETE" });
        state.stockedIds.delete(itemId);
      } else {
        await apiRequest(`/api/stocks/${itemId}`, { method: "PUT" });
        state.stockedIds.add(itemId);
      }
      updateStockButtonLabel(button, !alreadyStocked);
    } catch (error) {
      showError(error.message);
    }
  }

  // ---- ストック一覧 ----

  async function loadStocks() {
    clearError();
    els.stocksList.innerHTML = "<li class=\"item-card\">読み込み中...</li>";
    try {
      const items = await apiRequest("/api/stocks?per_page=50");
      state.stockedIds = new Set(items.map((item) => item.id));
      renderStocksList(items);
    } catch (error) {
      els.stocksList.innerHTML = "";
      showError(error.message);
    }
  }

  function renderStocksList(items) {
    els.stocksList.innerHTML = "";
    if (!items || items.length === 0) {
      els.stocksList.innerHTML = "<li class=\"item-card\">ストックされた記事はまだありません</li>";
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "item-card";

      const main = document.createElement("div");
      main.className = "item-card-main";
      main.innerHTML = `<p class="item-card-title"></p>`;
      main.querySelector(".item-card-title").textContent = item.title || "(無題)";
      main.addEventListener("click", () => openArticleDetail(item.id));

      const unstockButton = document.createElement("button");
      unstockButton.textContent = "解除する";
      unstockButton.addEventListener("click", async () => {
        clearError();
        try {
          await apiRequest(`/api/stocks/${item.id}`, { method: "DELETE" });
          state.stockedIds.delete(item.id);
          loadStocks();
        } catch (error) {
          showError(error.message);
        }
      });

      li.appendChild(main);
      li.appendChild(unstockButton);
      els.stocksList.appendChild(li);
    });
  }

  // ---- 下書き一覧・エディタ ----

  async function loadDrafts() {
    clearError();
    els.draftsList.innerHTML = "<li class=\"item-card\">読み込み中...</li>";
    try {
      const drafts = await apiRequest("/api/drafts");
      renderDraftsList(drafts);
    } catch (error) {
      els.draftsList.innerHTML = "";
      showError(error.message);
    }
  }

  function renderDraftsList(drafts) {
    els.draftsList.innerHTML = "";
    if (!drafts || drafts.length === 0) {
      els.draftsList.innerHTML = "<li class=\"item-card\">下書きはまだありません</li>";
      return;
    }
    drafts.forEach((draft) => {
      const li = document.createElement("li");
      li.className = "item-card";

      const main = document.createElement("div");
      main.className = "item-card-main";
      main.innerHTML = `
        <p class="item-card-title"></p>
        <p><span class="status-badge"></span></p>
      `;
      main.querySelector(".item-card-title").textContent = draft.title || "(無題)";
      const badge = main.querySelector(".status-badge");
      badge.textContent = statusLabel(draft.status);
      badge.classList.add(draft.status);
      main.addEventListener("click", () => openDraftEditor(draft));

      li.appendChild(main);
      els.draftsList.appendChild(li);
    });
  }

  function statusLabel(status) {
    if (status === "published") return "投稿済み";
    if (status === "sync_error") return "同期エラー";
    return "下書き";
  }

  function openDraftEditor(draft) {
    clearError();
    showView("draft-editor");
    state.currentDraftId = draft ? draft.id : null;

    els.draftId.value = draft ? draft.id : "";
    els.draftTitle.value = draft ? draft.title : "";
    els.draftTags.value = draft ? (draft.tags || []).join(",") : "";
    els.draftPrivate.checked = draft ? !!draft.qiita_private : false;
    els.draftBody.value = draft ? draft.body || "" : "";
    renderDraftPreview();

    const isPublished = !!(draft && draft.qiita_id);
    els.draftPublishButton.hidden = isPublished;
    els.draftSyncButton.hidden = !isPublished;
    els.draftDeleteButton.hidden = !draft;

    if (draft) {
      const statusText = `状態: ${statusLabel(draft.status)}`;
      const urlLink = draft.qiita_url
        ? ` / <a href="${escapeAttr(draft.qiita_url)}" target="_blank" rel="noopener">Qiitaで見る</a>`
        : "";
      els.draftStatusInfo.innerHTML = statusText + urlLink;
    } else {
      els.draftStatusInfo.textContent = "";
    }
  }

  function renderDraftPreview() {
    els.draftPreview.innerHTML = renderMarkdown(els.draftBody.value);
  }

  function collectDraftPayload() {
    const tags = els.draftTags.value
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);
    return {
      title: els.draftTitle.value.trim(),
      body: els.draftBody.value,
      tags,
      qiita_private: els.draftPrivate.checked,
    };
  }

  async function onSaveDraft(event) {
    event.preventDefault();
    clearError();
    const payload = collectDraftPayload();
    try {
      let saved;
      if (state.currentDraftId) {
        saved = await apiRequest(`/api/drafts/${state.currentDraftId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } else {
        saved = await apiRequest("/api/drafts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      openDraftEditor(saved);
    } catch (error) {
      showError(error.message);
    }
  }

  async function onPublishDraft() {
    if (!state.currentDraftId) {
      showError("先に下書きを保存してくだされ");
      return;
    }
    clearError();
    try {
      const saved = await apiRequest(`/api/drafts/${state.currentDraftId}/publish`, { method: "POST" });
      openDraftEditor(saved);
    } catch (error) {
      showError(error.message);
    }
  }

  async function onSyncDraft() {
    if (!state.currentDraftId) return;
    clearError();
    try {
      const saved = await apiRequest(`/api/drafts/${state.currentDraftId}/sync`, { method: "PUT" });
      openDraftEditor(saved);
    } catch (error) {
      showError(error.message);
    }
  }

  async function onDeleteDraft() {
    if (!state.currentDraftId) return;
    if (!window.confirm("この下書きを削除いたし候か？")) return;
    clearError();
    try {
      await apiRequest(`/api/drafts/${state.currentDraftId}`, { method: "DELETE" });
      showView("drafts");
      loadDrafts();
    } catch (error) {
      showError(error.message);
    }
  }

  // ---- ユーティリティ ----

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
  }

  function escapeAttr(value) {
    return String(value).replace(/"/g, "&quot;");
  }
})();
