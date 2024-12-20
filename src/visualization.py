
import matplotlib as plt
import seaborn as sns

def visualize_slice_sag(ct_list_new, masks_multilabel_list, slice_index=None):
    """Visualizes a single slice of the CT data and its corresponding mask"""
    if slice_index is None:
        slice_index=int(ct_list_new[0].shape[1]//2)
    plt.imshow(ct_list_new[1][:, :, slice_index], aspect=5, cmap="gray")
    plt.imshow(masks_multilabel_list[1][:, :, slice_index], aspect=5, cmap="gray", alpha=0.3)
    plt.show()
    
    
def visualize_slice_coronal(ct_list_new, masks_multilabel_list, slice_index=None):
    """Visualizes a single coronal slice of the CT data and its corresponding mask, using 2/3 of the dimension by default"""
    if slice_index is None:
        slice_index=int(ct_list_new[0].shape[1]*2/3)
    plt.imshow(ct_list_new[1][:, slice_index, :], aspect=5, cmap="gray")
    plt.imshow(masks_multilabel_list[1][:, slice_index, :], aspect=5, cmap="gray", alpha=0.3)
    plt.show()


def plot_mean_suv_by_spinal_level(mean_suv_by_vertebral_level_across_patients,label_to_spinal_level,palette="Blues"):
    "Plot mean SUV values by spinal level using a boxplot"
    data=[]
    labels=[]
    for label in sorted(mean_suv_by_vertebral_level_across_patients.keys()):
        spinal_level=label_to_spinal_level.get(label,f'Level {label}')
        data.append(mean_suv_by_vertebral_level_across_patients[label])
        labels.append(spinal_level)
    sns.set(style="whitegrid")
    palette_colors=sns.color_palette(palette,len(labels))
    plt.figure(figsize=(5,4))
    sns.boxplot(data=data,palette=palette_colors)
    plt.xticks(ticks=range(len(labels)),labels=labels,fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel('Spinal Level',fontsize=14)
    plt.ylabel('Mean SUV',fontsize=14)
    plt.title('Mean SUV by Spinal Level Across Patients',fontsize=16)
    plt.tight_layout()
    plt.show()
