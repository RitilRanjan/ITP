import subprocess
import sys

commands = [
    # 1. Create standard variables
    "cv z",
    "cv w",
    "cv u",
    "cv v",
    "cv y1",
    "cv y2",
    "cv E",

    # Register variables as terms in env.terms for substitutions
    "ct tx x",
    "ct ty y",
    "ct tz z",
    "ct tw w",
    "ct tu u",
    "ct tv v",
    "ct ty1 y1",
    "ct ty2 y2",
    "ct tE E",

    # Define and prove helper equalities
    "cf f_eq_z z = z",
    "ua E1 f_eq_z",
    "cf f_eq_w w = w",
    "ua E1 f_eq_w",
    "cf f_eq_v v = v",
    "ua E1 f_eq_v",

    # 2. Define the subset relation ⊆
    "cf f_sub ∀ z ( z ∈ x ⇒ z ∈ y )",
    "def_r 2 x ⊆ y f_sub",

    # 3. Prove subset is reflexive
    "cf f_ref ∀ x ( x ⊆ x )",
    "fold ⊆ 1 f_ref f_ref_expanded f_ref_equiv",
    "cf f_ref_core z ∈ x ⇒ z ∈ x",
    "ir PC1 f_ref_core",
    "cf f_eq_x x = x",
    "ua E1 f_eq_x",
    "cf f_imp x = x ⇒ (z ∈ x ⇒ z ∈ x)",
    "ir PC1 f_imp f_ref_core",
    "cf f_imp_quant x = x ⇒ ∀ z ( z ∈ x ⇒ z ∈ x )",
    "ir QR1 f_imp_quant f_imp",
    "cf f_ref_x ∀ z ( z ∈ x ⇒ z ∈ x )",
    "ir PC1 f_ref_x f_eq_x f_imp_quant",
    "cf f_eq_y y = y",
    "ua E1 f_eq_y",
    "cf f_y_imp_ref_x y = y ⇒ ∀ z ( z ∈ x ⇒ z ∈ x )",
    "ir PC1 f_y_imp_ref_x f_ref_x",
    "cf f_y_imp_ref_all y = y ⇒ ∀ x ( ∀ z ( z ∈ x ⇒ z ∈ x ) )",
    "ir QR1 f_y_imp_ref_all f_y_imp_ref_x",
    "cf f_ref_expanded ∀ x ( ∀ z ( z ∈ x ⇒ z ∈ x ) )",
    "ir PC1 f_ref_expanded f_eq_y f_y_imp_ref_all",
    "ir PC1 f_ref f_ref_expanded f_ref_equiv",

    # 4. Prove subset is transitive
    "cf f_trans ∀ x ∀ y ∀ w ( ( x ⊆ y ∧ y ⊆ w ) ⇒ x ⊆ w )",
    "fold ⊆ 1 f_trans f_trans_exp1 f_trans_eq1",
    "fold ⊆ 1 f_trans_exp1 f_trans_exp2 f_trans_eq2",
    "fold ⊆ 1 f_trans_exp2 f_trans_expanded f_trans_eq3",
    "cf f_inst1 ∀ z ( z ∈ x ⇒ z ∈ y ) ⇒ ( z ∈ x ⇒ z ∈ y )",
    "ua Q1 f_inst1",
    "cf f_inst2 ∀ z ( z ∈ y ⇒ z ∈ w ) ⇒ ( z ∈ y ⇒ z ∈ w )",
    "ua Q1 f_inst2",
    "cf f_imp_core ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ( z ∈ x ⇒ z ∈ w )",
    "ir PC1 f_imp_core f_inst1 f_inst2",
    "cf f_trans_core ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w )",
    "ir QR1 f_trans_core f_imp_core",
    "cf f_eq_u u = u",
    "ua E1 f_eq_u",
    "cf f_u_imp_trans u = u ⇒ ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir PC1 f_u_imp_trans f_trans_core",
    "cf f_u_imp_trans_w u = u ⇒ ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir QR1 f_u_imp_trans_w f_u_imp_trans",
    "cf f_trans_w ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir PC1 f_trans_w f_eq_u f_u_imp_trans_w",
    "cf f_u_imp_trans_y_quant u = u ⇒ ∀ y ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir QR1 f_u_imp_trans_y_quant f_u_imp_trans_w",
    "cf f_trans_y ∀ y ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir PC1 f_trans_y f_eq_u f_u_imp_trans_y_quant",
    "cf f_u_imp_trans_x_quant u = u ⇒ ∀ x ∀ y ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir QR1 f_u_imp_trans_x_quant f_u_imp_trans_y_quant",
    "cf f_trans_expanded ∀ x ∀ y ∀ w ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ w ) ) ⇒ ∀ z ( z ∈ x ⇒ z ∈ w ) )",
    "ir PC1 f_trans_expanded f_eq_u f_u_imp_trans_x_quant",
    "ir PC1 f_trans_exp2 f_trans_expanded f_trans_eq3",
    "ir PC1 f_trans_exp1 f_trans_exp2 f_trans_eq2",
    "ir PC1 f_trans f_trans_exp1 f_trans_eq1",

    # 5. Prove subset is antisymmetric
    "cf f_antisym ∀ x ∀ y ( ( x ⊆ y ∧ y ⊆ x ) ⇒ x = y )",
    "fold ⊆ 1 f_antisym f_antisym_exp1 f_antisym_eq1",
    "fold ⊆ 1 f_antisym_exp1 f_antisym_expanded f_antisym_eq2",
    "cf f_inst_z1 ∀ z ( z ∈ x ⇒ z ∈ y ) ⇒ ( z ∈ x ⇒ z ∈ y )",
    "ua Q1 f_inst_z1",
    "cf f_inst_z2 ∀ z ( z ∈ y ⇒ z ∈ x ) ⇒ ( z ∈ y ⇒ z ∈ x )",
    "ua Q1 f_inst_z2",
    "cf f_eqv_core ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ ( z ∈ x ⇔ z ∈ y )",
    "ir PC1 f_eqv_core f_inst_z1 f_inst_z2",
    "cf f_eqv_quant ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ ∀ z ( z ∈ x ⇔ z ∈ y )",
    "ir QR1 f_eqv_quant f_eqv_core",
    "cf f_ext_inst ∀ z ( z ∈ x ⇔ z ∈ y ) ⇒ x = y",
    "ua extension f_ext_inst",
    "cf f_antisym_core ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y",
    "ir PC1 f_antisym_core f_eqv_quant f_ext_inst",
    "cf f_u_imp_antisym u = u ⇒ ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y )",
    "ir PC1 f_u_imp_antisym f_antisym_core",
    "cf f_u_imp_antisym_y u = u ⇒ ∀ y ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y )",
    "ir QR1 f_u_imp_antisym_y f_u_imp_antisym",
    "cf f_antisym_y ∀ y ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y )",
    "ir PC1 f_antisym_y f_eq_u f_u_imp_antisym_y",
    "cf f_u_imp_antisym_x_quant u = u ⇒ ∀ x ∀ y ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y )",
    "ir QR1 f_u_imp_antisym_x_quant f_u_imp_antisym_y",
    "cf f_antisym_expanded ∀ x ∀ y ( ( ∀ z ( z ∈ x ⇒ z ∈ y ) ∧ ∀ z ( z ∈ y ⇒ z ∈ x ) ) ⇒ x = y )",
    "ir PC1 f_antisym_expanded f_eq_u f_u_imp_antisym_x_quant",
    "ir PC1 f_antisym_exp1 f_antisym_expanded f_antisym_eq2",
    "ir PC1 f_antisym f_antisym_exp1 f_antisym_eq1",

    # 6. Prove unique existence of empty set
    "cf f_uniq_exists ∃! x ∀ w ( ¬ ( w ∈ x ) )",
    "cf f_spec ∃ y ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) )",
    "ua specification f_spec",
    "cf f_inst ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) ) ⇒ ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) )",
    "ua Q1 f_inst",
    "cf f_imp_neg_y ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) ) ⇒ ¬ ( w ∈ y )",
    "ir PC1 f_imp_neg_y f_inst f_eq_w",
    "cf f_imp_forall_neg_y ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) ) ⇒ ∀ w ( ¬ ( w ∈ y ) )",
    "ir QR1 f_imp_forall_neg_y f_imp_neg_y",
    "cf f_exists_empty ∀ w ( ¬ ( w ∈ y ) ) ⇒ ∃ z ∀ w ( ¬ ( w ∈ z ) )",
    "ua Q2 f_exists_empty",
    "cf f_imp_exists_empty ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) ) ⇒ ∃ z ∀ w ( ¬ ( w ∈ z ) )",
    "ir PC1 f_imp_exists_empty f_imp_forall_neg_y f_exists_empty",
    "cf f_spec_imp_exists ( ∃ y ∀ w ( w ∈ y ⇔ w ∈ x ∧ ¬ ( w = w ) ) ) ⇒ ∃ z ∀ w ( ¬ ( w ∈ z ) )",
    "ir QR2 f_spec_imp_exists f_imp_exists_empty",
    "cf f_exists_empty_set ∃ z ∀ w ( ¬ ( w ∈ z ) )",
    "ir PC1 f_exists_empty_set f_spec f_spec_imp_exists",
    "cf f_inst_x ∀ w ( ¬ ( w ∈ x ) ) ⇒ ¬ ( w ∈ x )",
    "ua Q1 f_inst_x",
    "cf f_inst_y ∀ w ( ¬ ( w ∈ y ) ) ⇒ ¬ ( w ∈ y )",
    "ua Q1 f_inst_y",
    "cf f_equiv_empty ( ∀ w ( ¬ ( w ∈ x ) ) ∧ ∀ w ( ¬ ( w ∈ y ) ) ) ⇒ ( w ∈ x ⇔ w ∈ y )",
    "ir PC1 f_equiv_empty f_inst_x f_inst_y",
    "cf f_equiv_empty_quant ( ∀ w ( ¬ ( w ∈ x ) ) ∧ ∀ w ( ¬ ( w ∈ y ) ) ) ⇒ ∀ w ( w ∈ x ⇔ w ∈ y )",
    "ir QR1 f_equiv_empty_quant f_equiv_empty",
    
    # Define extension axiom instance for w
    "cf f_ext_inst_w ∀ w ( w ∈ x ⇔ w ∈ y ) ⇒ x = y",
    "ua extension f_ext_inst_w",
    
    "cf f_uniq_empty_core ( ∀ w ( ¬ ( w ∈ x ) ) ∧ ∀ w ( ¬ ( w ∈ y ) ) ) ⇒ x = y",
    "ir PC1 f_uniq_empty_core f_equiv_empty_quant f_ext_inst_w",
    
    # -------------------------------------------------------------------------
    # VERSION 1: Unique Existence Proof with y = x for fold
    # -------------------------------------------------------------------------
    "sf f_uniq_empty_core x tv f_uniq_vy",
    "sf f_uniq_vy y tz f_uniq_vz",
    "sf f_uniq_vz v ty f_uniq_yz",
    
    "cf f_e3_sym_vy v = y ∧ v = v ⇒ (v = v ⇒ y = v)",
    "ua E3 f_e3_sym_vy",
    "cf f_sym_vy v = y ⇒ y = v",
    "ir PC1 f_sym_vy f_e3_sym_vy f_eq_v",
    "cf f_e3_v1 w = w ∧ v = y ⇒ (w ∈ v ⇒ w ∈ y)",
    "ua E3 f_e3_v1",
    "cf f_e3_v2 w = w ∧ y = v ⇒ (w ∈ y ⇒ w ∈ v)",
    "ua E3 f_e3_v2",
    "cf f_eq_rel_v v = y ⇒ ( w ∈ v ⇔ w ∈ y )",
    "ir PC1 f_eq_rel_v f_e3_v1 f_e3_v2 f_eq_w f_sym_vy",
    "cf f_inst_v_empty ∀ w ( ¬ ( w ∈ v ) ) ⇒ ¬ ( w ∈ v )",
    "ua Q1 f_inst_v_empty",
    "cf f_uimp1 v = y ⇒ ( ∀ w ( ¬ ( w ∈ v ) ) ⇒ ¬ ( w ∈ y ) )",
    "ir PC1 f_uimp1 f_eq_rel_v f_inst_v_empty",
    "cf f_uimp1_alt ( v = y ∧ ∀ w ( ¬ ( w ∈ v ) ) ) ⇒ ¬ ( w ∈ y )",
    "ir PC1 f_uimp1_alt f_uimp1",
    "cf f_uimp1_quant ( v = y ∧ ∀ w ( ¬ ( w ∈ v ) ) ) ⇒ ∀ w ( ¬ ( w ∈ y ) )",
    "ir QR1 f_uimp1_quant f_uimp1_alt",
    "cf f_uimp1_final v = y ⇒ ( ∀ w ( ¬ ( w ∈ v ) ) ⇒ ∀ w ( ¬ ( w ∈ y ) ) )",
    "ir PC1 f_uimp1_final f_uimp1_quant",
    
    "cf f_e3_sym_yz y = z ∧ y = y ⇒ (y = y ⇒ z = y)",
    "ua E3 f_e3_sym_yz",
    "cf f_eq_y y = y",
    "ua E1 f_eq_y",
    "cf f_sym_yz y = z ⇒ z = y",
    "ir PC1 f_sym_yz f_e3_sym_yz f_eq_y",
    "cf f_e3_z1 w = w ∧ y = z ⇒ (w ∈ y ⇒ w ∈ z)",
    "ua E3 f_e3_z1",
    "cf f_e3_z2 w = w ∧ z = y ⇒ (w ∈ z ⇒ w ∈ y)",
    "ua E3 f_e3_z2",
    "cf f_eq_rel_yz y = z ⇒ ( w ∈ y ⇔ w ∈ z )",
    "ir PC1 f_eq_rel_yz f_e3_z1 f_e3_z2 f_eq_w f_sym_yz",
    
    "cf f_inst_z_empty ∀ w ( ¬ ( w ∈ z ) ) ⇒ ¬ ( w ∈ z )",
    "ua Q1 f_inst_z_empty",
    "cf f_imp_2 y = z ⇒ ( ∀ w ( ¬ ( w ∈ z ) ) ⇒ ¬ ( w ∈ y ) )",
    "ir PC1 f_imp_2 f_eq_rel_yz f_inst_z_empty",
    "cf f_imp_2_alt ( y = z ∧ ∀ w ( ¬ ( w ∈ z ) ) ) ⇒ ¬ ( w ∈ y )",
    "ir PC1 f_imp_2_alt f_imp_2",
    "cf f_imp_2_quant ( y = z ∧ ∀ w ( ¬ ( w ∈ z ) ) ) ⇒ ∀ w ( ¬ ( w ∈ y ) )",
    "ir QR1 f_imp_2_quant f_imp_2_alt",
    "cf f_imp_2_final y = z ⇒ ( ∀ w ( ¬ ( w ∈ z ) ) ⇒ ∀ w ( ¬ ( w ∈ y ) ) )",
    "ir PC1 f_imp_2_final f_imp_2_quant",
    
    # Propagate y=z equivalence using collision-free variable renaming
    "sf f_uimp1_final y tu f_uimp1_u",
    "sf f_uimp1_u v ty f_uimp1_y_temp",
    "sf f_uimp1_y_temp u tz f_uimp1_yz_final",
    
    "cf f_eq_empty_equiv y = z ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ ∀ w ( ¬ ( w ∈ z ) ) )",
    "ir PC1 f_eq_empty_equiv f_uimp1_yz_final f_imp_2_final",
    
    "cf f_uniq_exist_core ∀ w ( ¬ ( w ∈ z ) ) ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = z )",
    "ir PC1 f_uniq_exist_core f_uniq_yz f_eq_empty_equiv",
    "cf f_uniq_exist_y ∀ w ( ¬ ( w ∈ z ) ) ⇒ ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = z )",
    "ir QR1 f_uniq_exist_y f_uniq_exist_core",
    "cf f_q2_uniq ( ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = z ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = x )",
    "ua Q2 f_q2_uniq",
    "cf f_uniq_exist_x_yx ∀ w ( ¬ ( w ∈ z ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = x )",
    "ir PC1 f_uniq_exist_x_yx f_uniq_exist_y f_q2_uniq",
    "cf f_final_imp ( ∃ z ∀ w ( ¬ ( w ∈ z ) ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = x )",
    "ir QR2 f_final_imp f_uniq_exist_x_yx",
    "cf f_uniq_exists_expanded ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ y = x )",
    "ir PC1 f_uniq_exists_expanded f_exists_empty_set f_final_imp",
    
    # -------------------------------------------------------------------------
    # VERSION 2: Unique Existence Proof with x = y for Empty Set Subset
    # -------------------------------------------------------------------------
    "sf f_uniq_empty_core x tz f_uniq_zy",
    "cf f_uniq_yw_xy ( ∀ w ( ¬ ( w ∈ y ) ) ∧ ∀ w ( ¬ ( w ∈ z ) ) ) ⇒ z = y",
    "ir PC1 f_uniq_yw_xy f_uniq_zy",
    
    "cf f_e3_sym_zy z = y ∧ z = z ⇒ (z = z ⇒ y = z)",
    "ua E3 f_e3_sym_zy",
    "cf f_sym_zy z = y ⇒ y = z",
    "ir PC1 f_sym_zy f_e3_sym_zy f_eq_z",
    
    "cf f_e3_zy1 w = w ∧ z = y ⇒ (w ∈ z ⇒ w ∈ y)",
    "ua E3 f_e3_zy1",
    "cf f_e3_zy2 w = w ∧ y = z ⇒ (w ∈ y ⇒ w ∈ z)",
    "ua E3 f_e3_zy2",
    "cf f_eq_rel_zy z = y ⇒ ( w ∈ z ⇔ w ∈ y )",
    "ir PC1 f_eq_rel_zy f_e3_zy1 f_e3_zy2 f_eq_w f_sym_zy",
    
    "cf f_imp_zy z = y ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇒ ¬ ( w ∈ z ) )",
    "ir PC1 f_imp_zy f_eq_rel_zy f_inst_y",
    "cf f_imp_zy_alt ( z = y ∧ ∀ w ( ¬ ( w ∈ y ) ) ) ⇒ ¬ ( w ∈ z )",
    "ir PC1 f_imp_zy_alt f_imp_zy",
    "cf f_imp_zy_quant ( z = y ∧ ∀ w ( ¬ ( w ∈ y ) ) ) ⇒ ∀ w ( ¬ ( w ∈ z ) )",
    "ir QR1 f_imp_zy_quant f_imp_zy_alt",
    "cf f_imp_zy_final z = y ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇒ ∀ w ( ¬ ( w ∈ z ) ) )",
    "ir PC1 f_imp_zy_final f_imp_zy_quant",
    
    "sf f_uimp1_final v tz f_uimp1_z_final",
    
    "cf f_eq_empty_equiv_zy z = y ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ ∀ w ( ¬ ( w ∈ z ) ) )",
    "ir PC1 f_eq_empty_equiv_zy f_uimp1_z_final f_imp_zy_final",
    
    "cf f_uniq_exist_core_zy ∀ w ( ¬ ( w ∈ z ) ) ⇒ ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ z = y )",
    "ir PC1 f_uniq_exist_core_zy f_uniq_yw_xy f_eq_empty_equiv_zy",
    "cf f_uniq_exist_y_zy ∀ w ( ¬ ( w ∈ z ) ) ⇒ ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ z = y )",
    "ir QR1 f_uniq_exist_y_zy f_uniq_exist_core_zy",
    "cf f_q2_uniq_zy ( ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ z = y ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ x = y )",
    "ua Q2 f_q2_uniq_zy",
    "cf f_uniq_exist_z_xy ∀ w ( ¬ ( w ∈ z ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ x = y )",
    "ir PC1 f_uniq_exist_z_xy f_uniq_exist_y_zy f_q2_uniq_zy",
    "cf f_final_imp_xy ( ∃ z ∀ w ( ¬ ( w ∈ z ) ) ) ⇒ ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ x = y )",
    "ir QR2 f_final_imp_xy f_uniq_exist_z_xy",
    "cf f_uniq_exists_expanded_xy ∃ x ∀ y ( ∀ w ( ¬ ( w ∈ y ) ) ⇔ x = y )",
    "ir PC1 f_uniq_exists_expanded_xy f_exists_empty_set f_final_imp_xy",
    
    # Rename variables in empty set uniqueness version 2
    "sb f_uniq_exists_expanded_xy x tu f_uniq_exists_u",
    "sb f_uniq_exists_u y tv f_uniq_exists_uv",
    
    # fold f_uniq_exists version 1
    "fold ∃! 1 f_uniq_exists y f_uniq_exists_expanded f_uniq_exists_equiv",
    "ir PC1 f_uniq_exists f_uniq_exists_expanded f_uniq_exists_equiv",

    # 7. Define empty set as iota function of 0 arity
    "iota ∅ f_uniq_exists",

    # 8. Prove empty set is a subset of every set
    "cf f_empty_sub ∀ x ( ∅ ⊆ x )",
    "fold ⊆ 1 f_empty_sub f_empty_sub_exp1 f_empty_sub_eq1",
    "fold ∅ 1 f_empty_sub_exp1 u v f_empty_sub_expanded f_empty_sub_eq2",
    
    "cf f_iota_inst ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ( ∀ w ( ¬ ( w ∈ u ) ) ⇔ u = u )",
    "ua Q1 f_iota_inst",
    "cf f_w_inst ∀ w ( ¬ ( w ∈ u ) ) ⇒ ¬ ( z ∈ u )",
    "ua Q1 f_w_inst",
    "cf f_iota_taut ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ( z ∈ u ⇒ z ∈ x )",
    "ir PC1 f_iota_taut f_iota_inst f_w_inst f_eq_u",
    "cf f_iota_taut_z ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ∀ z ( z ∈ u ⇒ z ∈ x )",
    "ir QR1 f_iota_taut_z f_iota_taut",
    "cf f_iota_taut_xz ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x )",
    "ir QR1 f_iota_taut_xz f_iota_taut_z",
    
    "cf f_conj_core_all ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) )",
    "ir PC1 f_conj_core_all f_iota_taut_xz",
    "cf f_exists_u_all ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) ) ⇒ ∃ u ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) )",
    "ua Q2 f_exists_u_all",
    "cf f_iota_exists_all ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ⇒ ∃ u ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) )",
    "ir PC1 f_iota_exists_all f_conj_core_all f_exists_u_all",
    
    "cf f_exists_imp_exists_all ( ∃ u ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ⇒ ∃ u ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) )",
    "ir QR2 f_exists_imp_exists_all f_iota_exists_all",
    "cf f_empty_sub_expanded ∃ u ( ( ∀ v ( ∀ w ( ¬ ( w ∈ v ) ) ⇔ u = v ) ) ∧ ∀ x ∀ z ( z ∈ u ⇒ z ∈ x ) )",
    "ir PC1 f_empty_sub_expanded f_uniq_exists_uv f_exists_imp_exists_all",
    
    # Prove f_empty_sub using the equivalences!
    "ir PC1 f_empty_sub_exp1 f_empty_sub_expanded f_empty_sub_eq2",
    "ir PC1 f_empty_sub f_empty_sub_exp1 f_empty_sub_eq1",

    # 9. Prove unique existence of unary union
    "cf f_union_uniq ∃! y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "fold ∃! 1 f_union_uniq v f_union_uniq_expanded f_union_uniq_equiv",
    "cf f_union_exist ∃ y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ua union f_union_exist",
    "cf f_uinst1 ∀ z ( z ∈ y1 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ y1 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ua Q1 f_uinst1",
    "cf f_uinst2 ∀ z ( z ∈ y2 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ y2 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ua Q1 f_uinst2",
    "cf f_union_equiv ( ∀ z ( z ∈ y1 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ∧ ∀ z ( z ∈ y2 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ( z ∈ y1 ⇔ z ∈ y2 )",
    "ir PC1 f_union_equiv f_uinst1 f_uinst2",
    "cf f_union_equiv_quant ( ∀ z ( z ∈ y1 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ∧ ∀ z ( z ∈ y2 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ∀ z ( z ∈ y1 ⇔ z ∈ y2 )",
    "ir QR1 f_union_equiv_quant f_union_equiv",
    "cf f_ext_y1y2 ∀ z ( z ∈ y1 ⇔ z ∈ y2 ) ⇒ y1 = y2",
    "ua extension f_ext_y1y2",
    "cf f_union_uniq_core ( ∀ z ( z ∈ y1 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ∧ ∀ z ( z ∈ y2 ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ y1 = y2",
    "ir PC1 f_union_uniq_core f_union_equiv_quant f_ext_y1y2",
    
    # Rename variables in union uniqueness
    "sf f_union_uniq_core y1 tv f_union_uniq_vy",
    "sf f_union_uniq_vy y2 ty f_union_uniq_vy_final",
    
    # Prove v = y => ( \forall z (z \in v <=> \exists w...) <=> \forall z (z \in y <=> \exists w...) )
    "cf f_e3_sym_vy v = y ∧ v = v ⇒ (v = v ⇒ y = v)",
    "ua E3 f_e3_sym_vy",
    "cf f_sym_vy v = y ⇒ y = v",
    "ir PC1 f_sym_vy f_e3_sym_vy f_eq_v",
    "cf f_e3_v1 z = z ∧ v = y ⇒ (z ∈ v ⇒ z ∈ y)",
    "ua E3 f_e3_v1",
    "cf f_e3_v2 z = z ∧ y = v ⇒ (z ∈ y ⇒ z ∈ v)",
    "ua E3 f_e3_v2",
    "cf f_eq_rel_v v = y ⇒ ( z ∈ v ⇔ z ∈ y )",
    "ir PC1 f_eq_rel_v f_e3_v1 f_e3_v2 f_eq_z f_sym_vy",
    "cf f_inst_v ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ua Q1 f_inst_v",
    "cf f_uimp1 v = y ⇒ ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) )",
    "ir PC1 f_uimp1 f_eq_rel_v f_inst_v",
    "cf f_uimp1_alt ( v = y ∧ ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ir PC1 f_uimp1_alt f_uimp1",
    "cf f_uimp1_quant ( v = y ∧ ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ir QR1 f_uimp1_quant f_uimp1_alt",
    "cf f_uimp1_final v = y ⇒ ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) )",
    "ir PC1 f_uimp1_final f_uimp1_quant",
    "cf f_inst_y_new_union ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ua Q1 f_inst_y_new_union",
    "cf f_uimp2 v = y ⇒ ( ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) )",
    "ir PC1 f_uimp2 f_eq_rel_v f_inst_y_new_union",
    "cf f_uimp2_alt ( v = y ∧ ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ir PC1 f_uimp2_alt f_uimp2",
    "cf f_uimp2_quant ( v = y ∧ ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) )",
    "ir QR1 f_uimp2_quant f_uimp2_alt",
    "cf f_uimp2_final v = y ⇒ ( ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) )",
    "ir PC1 f_uimp2_final f_uimp2_quant",
    "cf f_eq_union_equiv v = y ⇒ ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) )",
    "ir PC1 f_eq_union_equiv f_uimp1_final f_uimp2_final",
    
    # Prove unique existence of union
    "cf f_union_uniq_exist_core ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ir PC1 f_union_uniq_exist_core f_union_uniq_vy_final f_eq_union_equiv",
    "cf f_union_uniq_exist_v ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ir QR1 f_union_uniq_exist_v f_union_uniq_exist_core",
    "cf f_q2_union ( ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y ) ) ⇒ ∃ y ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ua Q2 f_q2_union",
    "cf f_union_uniq_exist_y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇒ ∃ y ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ir PC1 f_union_uniq_exist_y f_union_uniq_exist_v f_q2_union",
    "cf f_union_final_imp ( ∃ y ∀ z ( z ∈ y ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ) ⇒ ∃ y ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ir QR2 f_union_final_imp f_union_uniq_exist_y",
    "cf f_union_uniq_expanded ∃ y ∀ v ( ∀ z ( z ∈ v ⇔ ∃ w ( z ∈ w ∧ w ∈ x ) ) ⇔ v = y )",
    "ir PC1 f_union_uniq_expanded f_union_exist f_union_final_imp",
    
    # Prove f_union_uniq from equivalence
    "ir PC1 f_union_uniq f_union_uniq_expanded f_union_uniq_equiv",

    # 10. Define unary union ∪ as iota function of 1 arity
    "iota ∪ f_union_uniq",
    
    # Exit REPL
    "exit"
]

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(script_dir, '..', 'main.py')

proc = subprocess.Popen(
    [sys.executable, main_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

for cmd in commands:
    print(f"Executing: {cmd}")
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()

stdout, stderr = proc.communicate()
print("\n--- STDOUT ---")
print(stdout)
print("--- STDERR ---")
print(stderr)
