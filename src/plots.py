import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import seaborn as sns
from matplotlib.ticker import MultipleLocator, MaxNLocator
from functools import partial
import os
import argparse

from file_structure import get_response_regression_analysis_fpath

### Process Data
def get_stat_table(fpath_kwargs, combined=False, significance_threshold=0.05):
    fpath_fxn = partial(get_response_regression_analysis_fpath, **fpath_kwargs)  
    if combined:
        fpath_fxn = partial(fpath_fxn, prompt_idx="all")
        stat_table = combine_control_tables(fpath_fxn)
    else:
        stat_table = combine_prompt_tables(fpath_fxn)
    add_significance_column(stat_table, significance_threshold=significance_threshold)
    return stat_table

def combine_control_tables(fpath_fxn):
    tables = []
    identities = ["age", "gender", "ethnicity", "education", "employment_status", "birth_region", "reside_region", "religion"]
    for identity in identities:
        table = pd.read_csv(fpath_fxn(formula_variable=f"{identity}_control"))
        table = table[table["classification_category"]==identity]
        tables.append(table)
    combined = pd.concat(tables, axis=0)
    return combined

def get_prompt_table(fpath_fxn, prompt_idx):
    return combine_control_tables(partial(fpath_fxn, prompt_idx=prompt_idx))
    
def combine_prompt_tables(fpath_fxn, prompt_idxs = list(range(250))):
    tables = []
    for prompt_idx in prompt_idxs:
        try:
            table = get_prompt_table(fpath_fxn, prompt_idx)
        except FileNotFoundError:
            continue
        except pd.errors.EmptyDataError:
            prompt_idx += 1
            continue
        table["prompt_idx"] = prompt_idx
        tables.append(table)
        prompt_idx += 1
    combined = pd.concat(tables, axis=0)
    return combined

def get_ci_columns(significance_threshold):
    sig_nums = [np.format_float_positional(significance_threshold*100/2, trim='0'), np.format_float_positional(100-significance_threshold*100/2, trim='0')]
    col_names = [f"{num} %" for num in sig_nums]
    return col_names

def add_significance_column(df, significance_threshold=0.05):
    col_names = get_ci_columns(significance_threshold)
    significant = np.array([False]*len(df))
    significant[np.sign(df[col_names[0]]) == np.sign(df[col_names[1]])] = True
    df["significant"] = significant



plt.style.use('tableau-colorblind10')

def plot_main_fig(data_dict):
    labels_to_spaced_labels = {
        "White (ref.)": "White\n(ref.)",
        "Male (ref.)": "Male\n(ref.)",
        "Non-Binary / Third Gender": "Non-\nBinary",
    }
    categories = data_dict['categories']
    models = data_dict['models']
    selected_identities = data_dict['selected_identities']
    coefficients = data_dict['coefficients']
    sensitivity_scores = data_dict['sensitivity_scores']
    identity_groups = data_dict['identities']
    
    identity_to_group = {}
    
    for i, (group_name, identities) in enumerate(identity_groups.items()):
        for identity in identities:
            identity_to_group[identity] = group_name
            

    group_colors = plt.cm.tab10(np.arange(len(models)))
    color_map = {}   
    for i, model in enumerate(models):
        color_map[model] = group_colors[i]
    
    model_markers = ['o', 's', '^', 'D', 'v', '>', '<', 'p']  
    model_alphas = [1,1,1,1]
    model_offset = 0.3 
    
    fig = plt.figure(figsize=(20, 14))
    
    gs = fig.add_gridspec(2, len(categories), height_ratios=[1, 1], 
                         hspace=0.35, wspace=0.45)
    
    def get_positions(identities, models):
        positions = {}
        group_offsets = {}
        current_pos = 0
        
        grouped = {}
        for identity in identities:
            group = identity_to_group.get(identity, 'unknown')
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(identity)
        
        for group_name in grouped.keys():
            group_offsets[group_name] = current_pos
            for i, identity in enumerate(grouped[group_name]):
                base_pos = current_pos + i * (len(models) * model_offset + 0.5)
                positions[identity] = {}
                for j, model in enumerate(models):
                    positions[identity][model] = base_pos + j * model_offset
            current_pos += len(grouped[group_name]) * (len(models) * model_offset + 0.5) + 1.0  # Add group spacing
        
        return positions, group_offsets
    
    positions, group_offsets = get_positions(selected_identities, models)
    
    for cat_idx, category in enumerate(categories):
        ax_coef = fig.add_subplot(gs[0, cat_idx])
        
        for identity in selected_identities:
            for model_idx, model in enumerate(models):
                if model in coefficients[category] and identity in coefficients[category][model]:
                    coef_val = coefficients[category][model].get(identity, 0)
                    ci_lower = coefficients[category][model].get(f"{identity}_ci_lower", coef_val - 0.05)
                    ci_upper = coefficients[category][model].get(f"{identity}_ci_upper", coef_val + 0.05)
                    
                    pos = positions[identity][model]
                    color = color_map.get(model, 'gray')
                    marker = model_markers[model_idx % len(model_markers)]
                    alpha = model_alphas[model_idx % len(model_alphas)]
                    
                    ax_coef.plot([ci_lower, ci_upper], [pos, pos], color=color, alpha=alpha*0.7, linewidth=2)
                    ax_coef.scatter(coef_val, pos, color=color, marker=marker, s=80, alpha=alpha, 
                                  zorder=3, edgecolors='white', linewidth=1, label=f'{model}' if identity == selected_identities[0] else "")
        
        ax_coef.axvline(x=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        
        identity_label_positions = []
        identity_labels = []
        for identity in selected_identities:
            center_pos = np.mean([positions[identity][model] for model in models])
            identity_label_positions.append(center_pos)
            identity_labels.append(identity if not identity in labels_to_spaced_labels else labels_to_spaced_labels[identity])
        
        ax_coef.set_yticks(identity_label_positions)
        ax_coef.set_yticklabels(identity_labels, fontsize=16)
        ax_coef.tick_params(axis='x', labelsize=14)
        ax_coef.xaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))    # Major ticks every 1 unit
        if category == "Salary Advice":
            ax_coef.set_xlabel('Coefficient (US Dollars)', fontsize=18)
        else:
            ax_coef.set_xlabel('Coefficient (Log Odds)', fontsize=18)
        ax_coef.set_title(f'{category.title()}\nBias', fontsize=18, fontweight='bold')
        ax_coef.grid(axis='x', alpha=0.5)
        
        if cat_idx == 0:
            model_legend_elements = []
            for i, model in enumerate(models):
                marker = model_markers[i % len(model_markers)]
                alpha = model_alphas[i % len(model_alphas)]
                model_legend_elements.append(plt.scatter([], [], marker=marker, s=80, alpha=alpha, 
                                                       color='gray', edgecolors='white', linewidth=1, label=model))
            ax_coef.legend(handles=[elem.legend_elements()[0] for elem in model_legend_elements], 
                          labels=models, loc='upper left', bbox_to_anchor=(0, 1), fontsize=18)
        
        ax_sens = fig.add_subplot(gs[1, cat_idx])
        
        for identity in selected_identities:
            for model_idx, model in enumerate(models):
                if model in sensitivity_scores[category] and identity in sensitivity_scores[category][model]:
                    sens_val = sensitivity_scores[category][model].get(identity, 0)
                    
                    pos = positions[identity][model]
                    color = color_map.get(model, 'gray')
                    alpha = model_alphas[model_idx % len(model_alphas)]
                    
                    ax_sens.barh(pos, sens_val, color=color, alpha=alpha, height=model_offset*0.8,
                               label=f'{model}' if identity == selected_identities[0] else "")
        
        ax_sens.set_yticks(identity_label_positions)
        ax_sens.set_yticklabels(identity_labels, fontsize=16)
        ax_sens.tick_params(axis='x', labelsize=14)
        ax_sens.set_xlabel('% of Questions Sensitive', fontsize=18)
        ax_sens.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=4))
        ax_sens.set_title(f'{category.title()}\nSensitivity Scores', fontsize=18, fontweight='bold')
        ax_sens.set_xlim(0, 1)
        ax_sens.grid(axis='x', alpha=0.5)

        if cat_idx == 0:
            group_label_positions = {}
            for group_name in identity_groups.keys():
                group_identities = [identity for identity in selected_identities 
                                  if identity_to_group.get(identity) == group_name]
                if group_identities:
                    group_positions = []
                    for identity in group_identities:
                        center_pos = np.mean([positions[identity][model] for model in models])
                        group_positions.append(center_pos)
                    group_center = np.mean(group_positions)
                    group_label_positions[group_name] = group_center
            
            for group_name, y_pos in group_label_positions.items():
                ax_coef.text(-0.5, y_pos, group_name, transform=ax_coef.get_yaxis_transform(),
                            fontsize=18, fontweight='bold', ha='center', va='center',
                            rotation=90, color='black')
            
            for group_name, y_pos in group_label_positions.items():
                ax_sens.text(-0.5, y_pos, group_name, transform=ax_sens.get_yaxis_transform(),
                            fontsize=18, fontweight='bold', ha='center', va='center',
                            rotation=90, color='black')
    
    fig.suptitle('Sociolinguistic Bias and Sensitivity Across LLM Applications', 
                 fontsize=24, fontweight='bold', y=0.97)
    
    legend_elements = []
    for model, color in zip(models, group_colors):
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, alpha=1, 
                                           label=model.replace('_', ' ').title()))
    
    fig.legend(handles=legend_elements, loc='center', bbox_to_anchor=(0.5, 0.04), 
              ncol=len(identity_groups), fontsize=18)
    
    plt.tight_layout()
    return fig

def get_main_fig_data(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fpath_kwargs):
    plot_data = {}
    plot_data["categories"] = prompt_type_names
    plot_data["models"] = model_names
    plot_data["coefficients"] = {}
    plot_data["sensitivity_scores"] = {}
    plot_data["identities"] = {}
    
    for prompt_type_name in prompt_type_names:
        plot_data["sensitivity_scores"][prompt_type_name] = {}
        plot_data["coefficients"][prompt_type_name] = {}
        for model_name in model_names:
            plot_data["sensitivity_scores"][prompt_type_name][model_name] = {
                f"{level} (ref.)": 0 for level in reference_levels.values()
            }
            plot_data["coefficients"][prompt_type_name][model_name] = {}
            for level in reference_levels.values():
                plot_data["coefficients"][prompt_type_name][model_name].update({
                    f"{level} (ref.)": 0, f"{level} (ref.)_ci_lower": 0,  f"{level} (ref.)_ci_upper": 0 
                })
    
    plot_data['selected_identities'] = ['Male (ref.)', 'Female', 'Non-Binary / Third Gender', 'White (ref.)', 'Asian', 'Black', 'Hispanic', 'Mixed']
    
    
    for prompt_type_idx, prompt_type in enumerate(prompt_types):
        for response_feature in prompt_type_to_response_feature[prompt_type]:
            fpath_kwargs["prompt_type"] = prompt_type
            model_tables = []
            for model_idx, model in enumerate(models):
                fpath_kwargs["generation_model"] = model
                stat_table = get_stat_table(fpath_kwargs, combined=True, significance_threshold=significance_threshold)
                stat_table = stat_table[stat_table["response_feature"] == response_feature]
                
                mult = 1
                if prompt_type == "salaries":
                    mult=1000
       
                ci_cols = get_ci_columns(significance_threshold)
                for identity_idx, identity in enumerate(stat_table["identity_variable"]):
                    id_category = stat_table["classification_category"].iloc[identity_idx].replace("_"," ").title()
                    if not id_category in plot_data["identities"]:
                        plot_data["identities"][id_category] = [f'{reference_levels[stat_table["classification_category"].iloc[identity_idx]]} (ref.)']
                    if not identity.title() in plot_data["identities"][id_category]:
                        plot_data["identities"][id_category] = plot_data["identities"][id_category] + [identity.title()]
                    plot_data["coefficients"][prompt_type_names[prompt_type_idx]][model_names[model_idx]][identity.title()] = stat_table["estimate"].iloc[identity_idx].item()*mult
                    plot_data["coefficients"][prompt_type_names[prompt_type_idx]][model_names[model_idx]][f"{identity.title()}_ci_lower"] = stat_table[ci_cols[0]].iloc[identity_idx].item()*mult
                    plot_data["coefficients"][prompt_type_names[prompt_type_idx]][model_names[model_idx]][f"{identity.title()}_ci_upper"] = stat_table[ci_cols[1]].iloc[identity_idx].item()*mult
    
                stat_table = get_stat_table(fpath_kwargs, combined=False, significance_threshold=significance_threshold)
                stat_table = stat_table[stat_table["response_feature"] == response_feature]
    
                for idx, (category, identity) in stat_table[["classification_category", "identity_variable"]].drop_duplicates().iterrows():
                    percent_sensitive = len(stat_table[(stat_table["classification_category"] == category) & (stat_table["identity_variable"] == identity) & (stat_table["p.value"]< 0.05)])/(1+np.max(stat_table["prompt_idx"]))
                    plot_data["sensitivity_scores"][prompt_type_names[prompt_type_idx]][model_names[model_idx]][identity.title()] = percent_sensitive
    return plot_data

def create_faceted_coefficient_plot(data, topic, reference_levels=None, figsize=None, 
                                   colors=None, save_path=None, ncols=2):
    models = sorted(data['model'].unique())
    variables = sorted(data['variable'].unique())
    n_vars = len(variables)
    
    nrows = (n_vars + ncols - 1) // ncols
    
    if figsize is None:
        figsize = (6 * ncols, 4 * nrows)
    
    if colors is None:
        colors = plt.cm.tab10(np.arange(len(models)))
    model_colors = dict(zip(models, colors))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    plt.subplots_adjust(top=0.85, hspace=0.3, wspace=0.4, left=0.01)  
    
    if nrows == 1 and ncols == 1:
        axes = [axes]
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for var_idx, variable in enumerate(variables):
        ax = axes[var_idx]
        var_data = data[data['variable'] == variable].copy()
        
        all_levels = sorted(var_data['level'].unique())
        
        ref_level = None
        if reference_levels and variable in reference_levels:
            ref_level = reference_levels[variable]
            if ref_level not in all_levels:
                all_levels.insert(0, ref_level)
        
        y_positions = []
        y_labels = []
        
        multiline_labels = {}
        for level in all_levels:
            label = level if level != ref_level or level in var_data['level'].values else f"{level} (ref)"
            if len(label) > 30:
                words = label.split()
                if len(words) > 1:
                    mid_point = len(words) // 2
                    line1 = ' '.join(words[:mid_point])
                    line2 = ' '.join(words[mid_point:])
                    multiline_labels[level] = f"{line1}\n{line2}"
                else:
                    mid_point = len(label) // 2
                    multiline_labels[level] = f"{label[:mid_point]}\n{label[mid_point:]}"
            else:
                multiline_labels[level] = label
        
        has_multiline = any('\n' in label for label in multiline_labels.values())
        spacing = 5.0 if has_multiline else 1.0
        
        for level_idx, level in enumerate(all_levels):
            level_data = var_data[var_data['level'] == level]
            
            base_y = level_idx * spacing
            
            if level == ref_level and level_data.empty:
                y_positions.append(base_y)
                y_labels.append(multiline_labels[level])
                
                for model_idx, model in enumerate(models):
                    y_pos = base_y + (model_idx - len(models)/2 + 0.5) * 0.15
                    marker = get_marker(model_idx)
                    ax.scatter(0, y_pos, color=model_colors[model], s=50, 
                             marker=marker, alpha=0.6, zorder=3,
                             edgecolors='black', linewidth=0.5)
            else:
                y_positions.append(base_y)
                y_labels.append(multiline_labels[level])
                
                for model_idx, model in enumerate(models):
                    model_data = level_data[level_data['model'] == model]
                    if not model_data.empty:
                        row = model_data.iloc[0]
                        y_pos = base_y + (model_idx - len(models)/2 + 0.5) * 0.15
                        
                        ax.plot([row['ci_lower'], row['ci_upper']], [y_pos, y_pos], 
                               color=model_colors[model], linewidth=2.5, alpha=0.7, zorder=2)
                        
                        marker = get_marker(model_idx)
                        ax.scatter(row['coefficient'], y_pos, 
                                 color=model_colors[model], s=60, 
                                 marker=marker, zorder=4, 
                                 edgecolors='white', linewidth=1)
        
        ax.axvline(x=0, color='black', linestyle='--', alpha=0.5, linewidth=1, zorder=1)
        ax.set_yticks(y_positions)
        
        ax.set_yticklabels(y_labels, ha='right', va='center')
        ax.tick_params(axis='y', which='major', pad=5, labelsize=14)
        
        ax.axvline(x=0, color='black', linestyle='--', alpha=0.5, linewidth=1, zorder=1)
        ax.set_title(variable.replace('_', ' ').title(), fontweight='bold', fontsize=16)
        ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

        ax.xaxis.set_major_locator(MaxNLocator(nbins=5, min_n_ticks=4))
        ax.tick_params(axis='x', labelsize=14)
        ax.grid(axis='x', alpha=0.5)
        
        if y_positions:
            min_y = min(y_positions)
            max_y = max(y_positions)
            padding = spacing * 0.4  # Adjust this factor as needed
            ax.set_ylim(min_y - padding, max_y + padding)
        else:
            ax.set_ylim(-0.5, 0.5)
        
        if var_idx >= (nrows - 1) * ncols:
            if topic == "salaries":
                ax.set_xlabel('Coefficient (US Dollars)', fontsize=16)
            else:
                ax.set_xlabel('Coefficient (Log Odds)', fontsize=16)
    
    for idx in range(n_vars, len(axes)):
        axes[idx].set_visible(False)
    
    legend_elements = []
    for model_idx, model in enumerate(models):
        marker = get_marker(model_idx)
        legend_elements.append(plt.Line2D([0], [0], marker=marker, color='w', 
                                        markerfacecolor=model_colors[model], 
                                        markersize=8, label=model.title(), 
                                        markeredgecolor='white', markeredgewidth=1))
    
    fig.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.05),
              ncol=len(models), frameon=True, fancybox=True, shadow=True, 
              title='Language Model', title_fontsize=16, fontsize=14)
    
    fig.suptitle(f'Sociolinguistic Bias in {topic.title()}', 
                fontsize=18, fontweight='bold', y=1.0, x=0.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    

def get_marker(model_idx):
    """Get marker style for each model"""
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    return markers[model_idx % len(markers)]

def create_coef_plots(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fig_dir, fpath_kwargs):
    outdir = os.path.join(fig_dir, "coef_plots")
    os.makedirs(outdir, exist_ok=True)
    for prompt_type_idx, prompt_type in enumerate(prompt_types):
        for response_feature in prompt_type_to_response_feature[prompt_type]:
            fpath_kwargs["prompt_type"] = prompt_type
            model_tables = []
            for model in models:
                fpath_kwargs["generation_model"] = model
                stat_table = get_stat_table(fpath_kwargs, combined=True, significance_threshold=significance_threshold)
                stat_table = stat_table[stat_table["response_feature"] == response_feature]
                subtable = pd.DataFrame()
                subtable["variable"] = stat_table["classification_category"]
                subtable["level"] = stat_table["identity_variable"]
                subtable["coefficient"] = stat_table["estimate"]
                ci_cols = get_ci_columns(significance_threshold)
                subtable["ci_lower"] = stat_table[ci_cols[0]]
                subtable["ci_upper"] = stat_table[ci_cols[1]]
                subtable["model"] = model
                if prompt_type == "salaries":
                    for col in ["coefficient", "ci_upper", "ci_lower"]:
                        subtable[col] *= 1000
                model_tables.append(subtable)
                
            data = pd.concat(model_tables, axis=0)
            outpath = os.path.join(outdir, f"{prompt_type}_{response_feature}_coef.png")
            create_faceted_coefficient_plot(data, prompt_type_names[prompt_type_idx], reference_levels=reference_levels, figsize=None, 
                           colors=None, save_path=outpath, ncols=2)

def fix_label(label):
    if len(label) > 20:
        words = label.split()
        if len(words) > 1:
            mid_point = len(words) // 2
            line1 = ' '.join(words[:mid_point])
            line2 = ' '.join(words[mid_point:])
            return f"{line1}\n{line2}"
        else:
            mid_point = len(label) // 2
            return f"{label[:mid_point]}\n{label[mid_point:]}"
    return label


def plot_separate_bars(df_sensitivity, topic, save_path=None, colors=None):
    df_sensitivity['sensitivity'] = df_sensitivity['sensitivity'].astype(float)
    
    demographics = df_sensitivity['variable'].unique()
    n_demographics = len(demographics)
    
    fig, axes = plt.subplots(nrows=(n_demographics + 1) // 2, ncols=2, figsize=(15, 5 * ((n_demographics + 1) // 2)))
    axes = axes.flatten()  
    
    for i, dem in enumerate(demographics):
        ax = axes[i]
        subset = df_sensitivity[df_sensitivity['variable'] == dem]
        reference = reference_levels[dem]
        reference = f"{reference} (ref.)"
        all_models = subset["model"].unique().tolist()
        new_cols = [[dem, reference, model, 0] for model in all_models]
        new_cols = pd.DataFrame(new_cols,columns=["variable", "level", "model", "sensitivity"])
        subset = pd.concat([new_cols, subset], axis=0)
        
        subset["multiline_level"] = [fix_label(label) for label in subset["level"]]
        
        sns.barplot(
            data=subset,
            x="multiline_level",
            y="sensitivity",
            hue="model",
            ax=ax,
            palette="tab10"
        )
        
        ax.set_title(f'{" ".join(dem.split("_")).title()}', fontsize=20)
        ax.set_xlabel("")
        ax.set_ylabel("% of Questions Sensitive", fontsize=18)
        ax.set_ylim(0,1)
        ax.tick_params(axis='x', rotation=60, which='both', length=4, labelsize=16)
        ax.tick_params(axis='y', labelsize=16)
        
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    handles, labels = ax.get_legend_handles_labels()
    for ax in axes:
        ax.get_legend().remove()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    fig.legend(handles, [label.title() for label in labels], loc='upper center', bbox_to_anchor=(0.5, 0.99),
              ncol=len(labels), frameon=True, fancybox=True, shadow=True, 
              title='Language Model', title_fontsize=18, fontsize=16)
    
    fig.suptitle(f'Sociolinguistic Sensitivity in {topic.title()}', 
                fontsize=22, fontweight='bold', y=1.01)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
      
def plot_sensitivities(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fig_dir, fpath_kwargs):
    outdir = os.path.join(fig_dir, "sensitivity_plots")
    os.makedirs(outdir, exist_ok=True)
    for prompt_type_idx, prompt_type in enumerate(prompt_types):
        for response_feature in prompt_type_to_response_feature[prompt_type]:
            fpath_kwargs["prompt_type"] = prompt_type
            sensitivity_table = []
            for model in models:
                fpath_kwargs["generation_model"] = model
                stat_table = get_stat_table(fpath_kwargs, combined=False, significance_threshold=significance_threshold)
                stat_table = stat_table[stat_table["response_feature"] == response_feature]
                subtable = pd.DataFrame()
                subtable["question_id"] = stat_table["prompt_idx"]
                subtable["variable"] = stat_table["classification_category"]
                subtable["level"] = stat_table["identity_variable"]
                subtable["estimate"] = stat_table["estimate"]
                subtable["p_value"] = stat_table["p.value"]
    
                for idx, (variable, level) in subtable[["variable", "level"]].drop_duplicates().iterrows():
                    percent_sensitive = len(subtable[(subtable["variable"] == variable) & (subtable["level"] == level) & (subtable["p_value"]< significance_threshold)])/(1+np.max(stat_table["prompt_idx"]))
                    sensitivity_table.append([variable, level, percent_sensitive, model])
    
            sensitivity_table = pd.DataFrame(sensitivity_table, columns = ["variable", "level", "sensitivity", "model"])
        
            outpath = os.path.join(outdir, f"{prompt_type}_{response_feature}_sensitivity.png")
            plot_separate_bars(sensitivity_table, prompt_type_names[prompt_type_idx], save_path=outpath)
                

reference_levels = {
    "age": "18-24 years old",
    "gender": "Male",
    "ethnicity": "White",
    "religion": "No Affiliation",
    "birth_region": "Europe",
    "reside_region": "Europe",
    "employment_status": "Working full-time",
    "education": "University Bachelors Degree",
}

models_to_model_names = {
    "llama3": "Llama3-70B-Instruct",
    "qwen3": "Qwen3-32B"
}

prompt_type_to_response_feature = {
    "medical": ["seek_help"],
    "benefits": ["eligible"],
    "political": ["liberal"],
    "legal": ["user_preferred"],
    "salaries": ["salary"],
}

prompt_type_to_name = {
    "salaries": "Salary Advice",
    "medical": "Medical Advice",
    "legal": "Legal Information",
    "benefits": "Government Benefit Eligibility",
    "political": "Politicized Information",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", required=True, nargs='+')
    parser.add_argument("--prompt_types", required=True, nargs='+')
    parser.add_argument("--prompt_prefix_type", required=False, default="prism", type=str)
    parser.add_argument("--label_type", required=False, default="ground_truth", type=str)
    # parser.add_argument("--significance_threshold", required=False, default=0.05, type=float)
    parser.add_argument("--data_dir", default="./data")
    args = parser.parse_args()
    
    
    
    fpath_kwargs = {
        "data_dir": args.data_dir,
        "prompt_prefix_type": args.prompt_prefix_type,
        "label_type": args.label_type,
    }

    prompt_types = args.prompt_types
    prompt_type_names = [prompt_type_to_name[prompt_type] for prompt_type in prompt_types]
    models = args.models
    model_names = [models_to_model_names[model] for model in models]
    significance_threshold = 0.05
    
    fig_dir = os.path.join(args.data_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    main_data =  get_main_fig_data(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fpath_kwargs)
    main_fig = plot_main_fig(main_data)
    plt.savefig(os.path.join(fig_dir, "main.png"), dpi=300, bbox_inches='tight')

    create_coef_plots(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fig_dir, fpath_kwargs)
    
    plot_sensitivities(prompt_types, prompt_type_names, prompt_type_to_response_feature, models, model_names, reference_levels, significance_threshold, fig_dir, fpath_kwargs)

if __name__ == "__main__":
    main()