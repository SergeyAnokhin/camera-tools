from ThreeShots import ThreeShots
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

#shots = ThreeShots.FromDir(None, 'Foscam\\Day_Cat_nomotionsnap')
shots = ThreeShots.FromDir(None, 'Foscam\\Day_Lilia_Gate')
#shots = ThreeShots.FromDir(None, 'Foscam\\Day_Sergey_trash_motioninplace')
#shots = ThreeShots.FromDir(None, 'Foscam\\Day_sergey_buggy')

# shots.shot1.CalcHaarBody()
# shots.shot2.CalcHaarBody()
# shots.shot3.CalcHaarBody()

shots.CalcContours()

shots.shot1.DrawContours()
shots.shot2.DrawContours()
shots.shot3.DrawContours()

shots.shot1.MagnifyMotion()
shots.shot2.MagnifyMotion()
shots.shot3.MagnifyMotion()

plt.figure(figsize=(12, 6.025))
gs1 = gridspec.GridSpec(2, 3, left=0, right=1, top=1,
                        bottom=0, wspace=0, hspace=0)

plt.subplot(gs1[2])
shots.shot1.show_plt()
plt.subplot(gs1[5])
shots.shot3.show_plt()

plt.subplot(gs1[:2,:2]) # 
shots.shot2.show_plt()

plt.tight_layout()
plt.margins(0)
plt.show()
#plt.savefig(filename, transparent = True, bbox_inches = 'tight', pad_inches = 0)
