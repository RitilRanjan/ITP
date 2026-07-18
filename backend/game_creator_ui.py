import streamlit as st
import os
import json
from github import Github
from github import Auth

GAMES_DIR = "games"

def render_game_creator():
    st.subheader("🛠️ Game Creator")
    
    if not os.path.exists(GAMES_DIR):
        os.makedirs(GAMES_DIR)
        
    games = [d for d in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, d))]
    
    if "gc_active_game" not in st.session_state:
        st.session_state.gc_active_game = None

    if st.session_state.gc_active_game is None:
        # Show Top Level View (List of Games)
        with st.expander("Create New Game", expanded=False):
            new_game_name = st.text_input("New Game Name")
            if st.button("Create"):
                if new_game_name and new_game_name not in games:
                    os.makedirs(os.path.join(GAMES_DIR, new_game_name))
                    st.success(f"Game '{new_game_name}' created!")
                    st.rerun()
                elif new_game_name in games:
                    st.error("Game already exists!")
                    
        st.markdown("### Existing Games")
        
        # GitHub PR Auth at top
        with st.expander("GitHub Pull Request Settings", expanded=False):
            github_token = st.text_input("GitHub Personal Access Token (PAT)", type="password")
            target_repo = st.text_input("Target Repository (e.g. ritilranjan/ITP)", value="ritilranjan/ITP")
            st.session_state.github_token = github_token
            st.session_state.target_repo = target_repo

        for g in games:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{g}**")
            with col2:
                if st.button("Edit Levels", key=f"edit_{g}"):
                    st.session_state.gc_active_game = g
                    st.rerun()
            with col3:
                if st.button("Submit PR", key=f"pr_{g}"):
                    submit_pr_for_game(g)
                    
    else:
        # We are inside a game, showing Level Creator
        game = st.session_state.gc_active_game
        st.button("⬅️ Back to Games", on_click=lambda: st.session_state.update(gc_active_game=None))
        st.markdown(f"### Levels for: **{game}**")
        
        game_dir = os.path.join(GAMES_DIR, game)
        # Find all levels, they are usually level1.json, level2.json...
        # We will parse the number
        level_files = [f for f in os.listdir(game_dir) if f.startswith("level") and f.endswith(".json")]
        level_files.sort(key=lambda x: int(x.replace("level", "").replace(".json", "")) if x.replace("level", "").replace(".json", "").isdigit() else 999)
        
        for idx, lf in enumerate(level_files):
            file_path = os.path.join(game_dir, lf)
            level_name = ""
            try:
                with open(file_path, "r") as f:
                    level_data = json.load(f)
                    level_name = level_data.get("name", "")
            except:
                pass
                
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                st.write(f"{lf} - **{level_name}**")
            with col2:
                if st.button("Edit", key=f"edit_l_{lf}"):
                    st.session_state.gc_active_level = lf
                    st.session_state.gc_is_new_level = False
                    st.rerun()
            with col3:
                if idx > 0 and st.button("↑ Up", key=f"up_{lf}"):
                    swap_levels(game_dir, level_files, idx, idx-1)
                    st.rerun()
            with col4:
                if idx < len(level_files) - 1 and st.button("↓ Down", key=f"down_{lf}"):
                    swap_levels(game_dir, level_files, idx, idx+1)
                    st.rerun()
                    
        st.markdown("---")
        if st.button("➕ Create New Level"):
            new_idx = len(level_files) + 1
            new_level_filename = f"level{new_idx}.json"
            st.session_state.gc_active_level = new_level_filename
            st.session_state.gc_is_new_level = True
            st.rerun()
            
        if "gc_active_level" in st.session_state and st.session_state.gc_active_level:
            render_level_editor(game_dir, st.session_state.gc_active_level)

def render_level_editor(game_dir, filename):
    st.markdown(f"#### Editing {filename}")
    file_path = os.path.join(game_dir, filename)
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        # Default skeleton
        data = {
            "id": filename.replace(".json", ""),
            "name": "",
            "guide_hints": [""],
            "allowed_commands": ["cv", "cf", "ct", "cp", "mission", "apply", "show", "help", "intro", "fold", "and", "iff", "left", "right"],
            "allowed_axioms": ["E1", "E2", "E3", "Q1", "Q2"],
            "allowed_rules": ["QR1", "QR2", "PC1", "PC2"],
            "goal_statement": "",
            "start_env_commands": None,
            "theory": "NT"
        }
        
    with st.form("level_editor_form"):
        name = st.text_input("Level Name", value=data.get("name", ""))
        theory = st.selectbox("Theory", ["NT", "ZFC"], index=0 if data.get("theory") == "NT" else 1)
        goal_statement = st.text_input("Goal Statement", value=data.get("goal_statement", ""))
        
        st.markdown("**Hints (One per line)**")
        hints_str = "\n".join(data.get("guide_hints", []))
        hints_input = st.text_area("Hints", value=hints_str, height=150)
        
        st.markdown("**Environment State Setup**")
        st.info("Because the environment is complex, please write it as a list of ITP commands that should be executed to build the starting environment (e.g., `cv x y\\ncf p x=x`). The app will construct it.")
        start_env_val = "
".join(data.get("start_env_commands")) if data.get("start_env_commands") else ""
        start_env_input = st.text_area("Start Env Commands (One command per line)", value=start_env_val)
        
        # Multiselects
        from backend.Registry import AXIOMS, RULES
        all_axioms = list(AXIOMS.keys())
        all_rules = list(RULES.keys())
        all_cmds = ["cv", "cf", "ct", "cp", "mission", "apply", "show", "help", "intro", "fold", "and", "iff", "left", "right", "swap_eq", "imply", "contra", "auto", "search", "backward_search", "advanced_search", "and2", "intro2", "neg-", "neg+", "simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi", "st", "sf", "sb", "sa", "sp"]
        
        sel_axioms = st.multiselect("Allowed Axioms", all_axioms, default=[x for x in data.get("allowed_axioms", []) if x in all_axioms])
        sel_rules = st.multiselect("Allowed Rules", all_rules, default=[x for x in data.get("allowed_rules", []) if x in all_rules])
        sel_cmds = st.multiselect("Allowed Commands", all_cmds, default=[x for x in data.get("allowed_commands", []) if x in all_cmds])
        
        if st.form_submit_button("💾 Save and Exit"):
            data["name"] = name
            data["theory"] = theory
            data["goal_statement"] = goal_statement
            data["guide_hints"] = [h.strip() for h in hints_input.split("\n") if h.strip()]
            data["start_env_commands"] = [cmd.strip() for cmd in start_env_input.split("
") if cmd.strip()] if start_env_input.strip() else None
            data["allowed_axioms"] = sel_axioms
            data["allowed_rules"] = sel_rules
            data["allowed_commands"] = sel_cmds
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
                
            st.session_state.gc_active_level = None
            st.rerun()

def swap_levels(game_dir, level_files, idx1, idx2):
    file1 = os.path.join(game_dir, level_files[idx1])
    file2 = os.path.join(game_dir, level_files[idx2])
    
    try:
        import json
        with open(file1, "r") as f:
            data1 = json.load(f)
        with open(file2, "r") as f:
            data2 = json.load(f)
            
        # Swap the IDs so they still match their filenames
        new_id1 = level_files[idx2].replace(".json", "")
        new_id2 = level_files[idx1].replace(".json", "")
        
        data1["id"] = new_id1
        data2["id"] = new_id2
        
        # Save data2 to file1, and data1 to file2
        with open(file1, "w") as f:
            json.dump(data2, f, indent=2)
        with open(file2, "w") as f:
            json.dump(data1, f, indent=2)
    except Exception as e:
        print(f"Error swapping levels: {e}")

def submit_pr_for_game(game_name):
    token = st.session_state.get("github_token", "")
    repo_name = st.session_state.get("target_repo", "")
    
    if not token or not repo_name:
        st.error("Please provide GitHub PAT and Target Repo in the settings above!")
        return
        
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo(repo_name)
        
        branch_name = f"game-{game_name.replace(' ', '-')}"
        
        # Check if branch exists
        try:
            repo.get_branch(branch_name)
            branch_exists = True
        except:
            branch_exists = False
            
        main_ref = repo.get_git_ref("heads/main")
        
        if not branch_exists:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_ref.object.sha)
            
        # Get all files for the game
        game_dir = os.path.join(GAMES_DIR, game_name)
        
        for root, _, files in os.walk(game_dir):
            for file in files:
                file_path = os.path.join(root, file)
                repo_path = file_path # Keep the same path in repo
                
                with open(file_path, "r") as f:
                    content = f.read()
                    
                try:
                    contents = repo.get_contents(repo_path, ref=branch_name)
                    repo.update_file(contents.path, f"Update {file}", content, contents.sha, branch=branch_name)
                except:
                    repo.create_file(repo_path, f"Add {file}", content, branch=branch_name)
                    
        if not branch_exists:
            repo.create_pull(
                title=f"Add Game: {game_name}",
                body=f"This PR was automatically generated by the ITP Game Creator for the game '{game_name}'.",
                head=branch_name,
                base="main"
            )
            st.success(f"Pull Request created for {game_name}!")
        else:
            st.success(f"Updated existing branch {branch_name} for {game_name}!")
            
    except Exception as e:
        st.error(f"GitHub API Error: {e}")
