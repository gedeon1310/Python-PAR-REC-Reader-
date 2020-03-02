#%%
import pandas as pd
import os
import numpy as np
import re

class PAR_REC:    
    def __init__(self,par_filename,rec_filename =  None):
        self.PAR_path = par_filename
        self.REC_path = rec_filename
        if self.REC_path is None:
            # We assume REC file has same path as related PAR file, only extension changes
            self.REC_path = os.path.splitext(self.PAR_path)[0]+ '.REC'
            
        self.Sequence_info,self.General_Params = PAR_REC.PAR_to_Dataframe(self.PAR_path)
        self.Images = PAR_REC.REC_to_sequence(self.REC_path,self.Sequence_info)
        
        
    @staticmethod
    def PAR_to_Dataframe (par_file):
        # Read PAR file
        with open(par_file,'r') as f:
            PAR = f.read()
        
        # Split PAR file text into lines and extract columns names
        
        lines = PAR.split('\n')
        def_lines = [l.replace('#','').replace('*','').strip() for l in lines[55:96]]
        data_types = []
        n_cols = []
        full_names = []    
        for l in def_lines:
            current_type = re.findall(re.escape('(') + '\w*' + re.escape(')'),l)[-1][1:-1]
            if 'integer' in current_type:
               current_dtype = 'int'
               data_types.append(current_dtype)
            else:
                current_dtype  = 'float'
                data_types.append('float')
            
            full_names.append(l.split('(')[0].strip().replace(' ','_'))
            try: 
                n_cols.append(np.int16(current_type[0]))
                for ii in range(np.int16(current_type[0])-1):
                    data_types.append(current_dtype)                
            except:
                n_cols.append(1)
        
        
        # 1 - Extract data lines from PAR file and create corresponding array
        data_lines = lines[100:-3]
        data = None    
        for line in data_lines:
            values = np.array([float(p) for p in line.replace('#','').split(' ') if len(p)>0])
            values = values.reshape(-1,values.shape[0])    
            if data is None:
                data = values
            else:
                data =np.concatenate((data,values),axis = 0)
        
        # 2 - Define list of suffixes vs number columns per parameters, based on given informations
        suffixes_2cols = ['_x','_y']
        suffixes_3cols = ['_ap','_fh','_rl']    
        # 3 - Build final list of parameters with appropriate names and suffixes
        final_cols = []
        for param,n_col in zip(full_names,n_cols):
            if n_col == 1:
                final_cols.append(param)
            elif n_col == 2:
                for suff in suffixes_2cols:
                    final_cols.append(param + suff)        
            elif n_col == 3:
                for suff in suffixes_3cols:
                    final_cols.append(param + suff)
        # 4- Build final Dataframe and cast columns to accordingly to detected types:
        df = pd.DataFrame(data,columns = final_cols)
        for c,dtype in zip(df.columns,data_types):
            if dtype == 'int':
                df[c] = df[c].astype(np.int16)
            elif dtype == 'float':        
                df[c] = df[c].astype(np.float32)
                
                
        #Extract general parameters associated to the acquisition, build as Dictionary
        general_params = dict()
        general_params_lines =  [l.replace('.','').strip() for l in lines if l.startswith('.')]
        for l in general_params_lines:
            general_params[l.split(':')[0].strip()] = l.split(':')[1].strip()
            
        return(df,general_params)
        
    @staticmethod
    def REC_to_sequence(rec_file,df_par):
    # Read REC file
        with open(rec_file,'r') as f:
            REC = np.fromfile(f, dtype=np.uint16)        
        # Check if all images of the sequence have the same dimensions:
        Constant_img_dims = (len(df_par.recon_resolution_x.unique()) ==1) & (len(df_par.recon_resolution_y.unique()) ==1)
        # Reshape REC file array using images dimensions
        
        if Constant_img_dims:
            # Reshape whole array into 3D array
            sequence_shape = (df_par.shape[0],df_par.recon_resolution_y.values[0],df_par.recon_resolution_x.values[0])
            images = REC.reshape(sequence_shape).swapaxes(2,0).swapaxes(0,1)
        else:
            # Sequentially extract and reshape arrays to build images from initial REC values
            images = []
            for ii in range(df_par.shape[0]):
                x_dim = df_par.recon_resolution_x.values[ii]
                y_dim = df_par.recon_resolution_y.values[ii]
                npixels = x_dim * y_dim 
                new_im = REC[ii*npixels:(ii+1)*npixels].reshape((y_dim,x_dim))
                self.Images.append(new_im)
        return(images)
        
    def View_samples(self,Nplots = 6,n_cols = 3):
        # !!! Works only for constant dimensions over sequence
        from matplotlib import pyplot as plt
        
        inds = np.linspace(0,self.Images.shape[2]-1,Nplots).astype(int)
        f,ax = plt.subplots(Nplots//n_cols,n_cols,figsize = (25,10))
        for ii,ind in enumerate(inds):
#            row,col = ind2num(ii,shape[1])
            ax[ii//n_cols,ii%n_cols].imshow(self.Images[:,:,ind],cmap = 'gray')
            ax[ii//n_cols,ii%n_cols].set_axis_off()
            ax[ii//n_cols,ii%n_cols].set_title("Image {}".format(ind))
        f.tight_layout()
        
