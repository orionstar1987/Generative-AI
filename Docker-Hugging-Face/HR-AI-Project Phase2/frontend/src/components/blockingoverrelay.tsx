import { BeatLoader } from "react-spinners";

const BlockingOverlay = () => {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)', // semi-transparent black
          zIndex: 9999, // make sure it's above other elements
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
          <BeatLoader
                            loading={true}
                            size={15}
                            aria-label="Loading Spinner"
                            data-testid="loader"
                        ></BeatLoader>
      </div>
    );
  };
  
  export default BlockingOverlay;