## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2299 | 0.37 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0426 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2607 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.230) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.008
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: retract_lift
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.230
- **task_score** (E): 0.368
- **fitness_score**: 0.323  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2516 |
| contact_peg | 1.00 | 1.00 | 0.0189 |
| push_channel | 0.00 | 1.00 | 0.0552 |
| retract_lift | 0.33 | 1.00 | 0.1093 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.131, 0.060) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 | 1.00 / 1.333 | 105.322 | 162.327 |
| contact_peg | contact | 1.00 / force_exceeded | (0.516, 0.131, 0.060)→(0.512, 0.115, 0.050) | (0.505, 0.084, 0.034)→(0.505, 0.080, 0.035) | 0.164→0.160 | 1.00 / 2.333 | 50.397 | 35.240 |
| push_channel | push | 0.00 / step_budget | (0.512, 0.115, 0.050)→(0.521, 0.078, 0.066) | (0.505, 0.080, 0.035)→(0.507, 0.027, 0.031) | 0.160→0.108 | 1.00 / 3.667 | 407.142 | 867.295 |
| retract_lift | retract | 0.33 / step_budget | (0.521, 0.078, 0.066)→(0.509, -0.025, 0.099) | (0.507, 0.027, 0.031)→(0.506, -0.003, 0.025) | 0.108→0.079 | 1.00 / 1.000 | 1.341 | 712.220 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.516
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.268
- phase_score: 0.302
- phase_breakdown.contact_score: 0.733
- phase_breakdown.push_score: 0.036
- phase_breakdown.approach_score: 0.671

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.485
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.710
- **Median Q (composite search score)**: 0.225
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.374


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97015,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10649,"contact_peg.contact_force":7.18905,"contact_peg.contact_speed":0.02847,"push_channel.push_speed":0.07772},"optimized_scores":{"best_composite_score":0.18625,"best_fitness_score":0.19625,"best_task_score":0.1261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":825.0,"contact_point_centroid":[0.47496,0.11993,0.05983],"force_p95":622.37661,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.65516,"mean_force":401.6218,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51329,0.08839,0.04395]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":333.0,"contact_point_centroid":[0.47493,0.11989,0.05702],"force_p95":545.32797,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":716.63557,"mean_force":507.94517,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51322,0.0806,0.05067]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":882.0,"contact_point_centroid":[0.52504,0.08987,0.04591],"force_p95":465.73094,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":668.21111,"mean_force":268.32093,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51336,0.08792,0.04459]},{"body_a":"world","body_b":"link7","contact_count":556.0,"contact_point_centroid":[0.50249,0.15357,-4e-05],"force_p95":260.78724,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":524.65369,"mean_force":209.91949,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51242,0.08864,0.04934]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":848.0,"contact_point_centroid":[0.5252,0.09308,0.05066],"force_p95":354.15819,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.32059,"mean_force":238.8166,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51306,0.08613,0.05021]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.53638,0.11977,0.05936],"force_p95":463.24964,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":481.58207,"mean_force":361.57114,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5287,0.12828,0.06162]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54943,0.11955,0.05931],"force_p95":439.48531,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":440.21532,"mean_force":337.94625,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49276,0.1319,0.02704]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.5367,0.11987,0.05966],"force_p95":98.34328,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.34328,"mean_force":98.34328,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52908,0.12853,0.0623]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.50824,0.06875,0.05829],"force_p95":5.50538,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.56359,"mean_force":2.79473,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51397,0.07802,0.05361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52502,0.05108,0.05958],"force_p95":36.49832,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.33596,"mean_force":5.46263,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51394,0.0787,0.05299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":944.0,"contact_point_centroid":[0.50428,0.06045,0.00966],"force_p95":2.06981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.67645,"mean_force":0.9054,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51174,0.08993,0.04836]},{"body_a":"attachment","body_b":"peg","contact_count":318.0,"contact_point_centroid":[0.50614,0.08989,0.05129],"force_p95":5.3147,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.56659,"mean_force":1.37611,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5116,0.09046,0.04818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":981.0,"contact_point_centroid":[0.50689,0.05817,0.00945],"force_p95":0.88258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.94859,"mean_force":0.6542,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5134,0.08591,0.04559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.50567,0.08085,0.00935],"force_p95":0.56032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5149,0.1605,0.16815]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":226.0,"contact_point_centroid":[0.52513,0.07093,0.03809],"force_p95":1.31007,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.98825,"mean_force":0.37196,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51118,0.09004,0.04707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50034,0.198,0.29361]}],"total_contact_groups":17},"final_pose_error":0.08752,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50671,0.0148,0.02665],"final_tcp_position":[0.51274,-0.01267,0.08556],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":908.65516,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":314.86685,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":544.0,"raw_peak_contact_force":481.58207,"subtask_id":"approach","tcp_end":[0.52908,0.12853,0.0623],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":98.34328,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":98.34328,"tcp_end":[0.52916,0.12856,0.06236],"tcp_start":[0.52908,0.12853,0.0623],"tcp_to_object_dist_end":0.06022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,0.06054,0.0338],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.14085,"object_to_goal_dist_start":0.16113,"object_z_max":0.03646,"peak_contact_force":542.27292,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3244.0,"raw_peak_contact_force":716.63557,"tcp_end":[0.51336,0.08192,0.04991],"tcp_start":[0.52916,0.12856,0.06236],"tcp_to_object_dist_end":0.02753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,0.0148,0.02665],"object_pos_start":[0.50693,0.06054,0.0338],"object_to_goal_dist_end":0.09597,"object_to_goal_dist_start":0.14085,"object_z_max":0.0408,"peak_contact_force":2.74559,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2771.0,"raw_peak_contact_force":908.65516,"tcp_end":[0.51274,-0.01267,0.08556],"tcp_start":[0.51336,0.08192,0.04991],"tcp_to_object_dist_end":0.06528,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63889,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06955,"contact_peg.contact_force":13.69451,"contact_peg.contact_speed":0.02345,"push_channel.push_speed":0.07822},"optimized_scores":{"best_composite_score":0.27858,"best_fitness_score":0.28858,"best_task_score":0.26806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":901.0,"contact_point_centroid":[0.47181,0.11971,0.05988],"force_p95":610.92809,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1069.28803,"mean_force":308.28281,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5132,0.09357,0.04625]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54644,0.11971,0.05929],"force_p95":689.14634,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":775.66222,"mean_force":393.55502,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49077,0.12848,0.02904]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":490.0,"contact_point_centroid":[0.52502,0.09696,0.04743],"force_p95":441.59149,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.4359,"mean_force":298.74172,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51362,0.09363,0.04624]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.47497,0.11995,0.0579],"force_p95":397.47194,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.75693,"mean_force":221.80923,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51194,0.08469,0.05084]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52507,0.09643,0.05352],"force_p95":499.85538,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.38297,"mean_force":307.96615,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51244,0.09712,0.04927]},{"body_a":"world","body_b":"link7","contact_count":901.0,"contact_point_centroid":[0.49524,0.1588,-9e-05],"force_p95":313.79341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":450.61658,"mean_force":253.19996,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5101,0.09495,0.0491]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.49308,0.14686,-3e-05],"force_p95":401.7169,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.24731,"mean_force":277.97032,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51344,0.08543,0.05104]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47498,0.11225,0.02326],"force_p95":95.90313,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.12255,"mean_force":93.9284,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48635,0.10891,0.02148]},{"body_a":"peg","body_b":"channel_base_body","contact_count":929.0,"contact_point_centroid":[0.5045,0.06586,0.00982],"force_p95":2.00872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.343,"mean_force":1.02672,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50913,0.09723,0.04803]},{"body_a":"attachment","body_b":"peg","contact_count":601.0,"contact_point_centroid":[0.50425,0.09318,0.05057],"force_p95":2.68952,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.33249,"mean_force":1.43747,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5099,0.09435,0.04868]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":384.0,"contact_point_centroid":[0.52513,0.07161,0.03846],"force_p95":2.59113,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.3692,"mean_force":1.08943,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50837,0.09157,0.04711]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.50503,0.08365,0.0578],"force_p95":11.76051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.78272,"mean_force":2.3013,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51288,0.08722,0.0504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":982.0,"contact_point_centroid":[0.50675,0.05956,0.0093],"force_p95":0.9824,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.74414,"mean_force":0.64888,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51313,0.09075,0.04733]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":255.0,"contact_point_centroid":[0.52501,0.06631,0.0568],"force_p95":0.25638,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.14527,"mean_force":0.12796,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51334,0.09589,0.04534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.50413,0.09639,0.0096],"force_p95":3.20612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.01192,"mean_force":1.34512,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51224,0.13617,0.04839]},{"body_a":"attachment","body_b":"peg","contact_count":148.0,"contact_point_centroid":[0.50859,0.11954,0.04654],"force_p95":3.16762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.5619,"mean_force":2.16509,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51073,0.1313,0.04578]}],"total_contact_groups":18},"final_pose_error":0.10139,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50628,0.022,0.02406],"final_tcp_position":[0.51208,0.00089,0.08008],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1069.28803,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.1046,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55263,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51872,0.14878,0.05866],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50411,0.09953,0.03515],"object_pos_start":[0.50584,0.1046,0.03383],"object_to_goal_dist_end":0.17964,"object_to_goal_dist_start":0.18479,"object_z_max":0.03525,"peak_contact_force":50.48291,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":513.0,"raw_peak_contact_force":5.01192,"tcp_end":[0.51009,0.12869,0.0446],"tcp_start":[0.51872,0.14878,0.05866],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.06617,0.03534],"object_pos_start":[0.50411,0.09953,0.03515],"object_to_goal_dist_end":0.14641,"object_to_goal_dist_start":0.17964,"object_z_max":0.03984,"peak_contact_force":393.32446,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3092.0,"raw_peak_contact_force":775.66222,"tcp_end":[0.51344,0.08544,0.05099],"tcp_start":[0.51009,0.12869,0.0446],"tcp_to_object_dist_end":0.02565,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50628,0.022,0.02406],"object_pos_start":[0.507,0.06617,0.03534],"object_to_goal_dist_end":0.10343,"object_to_goal_dist_start":0.14641,"object_z_max":0.04082,"peak_contact_force":0.67294,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2687.0,"raw_peak_contact_force":1069.28803,"tcp_end":[0.51208,0.00089,0.08008],"tcp_start":[0.51344,0.08544,0.05099],"tcp_to_object_dist_end":0.06014,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43114,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09761,"contact_peg.contact_force":11.84642,"contact_peg.contact_speed":0.0133,"push_channel.push_speed":0.1188},"optimized_scores":{"best_composite_score":0.22475,"best_fitness_score":0.48475,"best_task_score":0.7105},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":680.0,"contact_point_centroid":[0.52711,0.11914,0.05993],"force_p95":326.48961,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1109.58698,"mean_force":294.48988,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52735,0.06412,0.09271]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52575,0.07902,0.05963],"force_p95":953.4334,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":969.68582,"mean_force":514.75426,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50293,0.07511,0.03866]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.52501,0.11995,0.05995],"force_p95":134.95761,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.71588,"mean_force":108.4201,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5352,0.06437,0.09745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.50549,-0.04089,0.00836],"force_p95":0.78925,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.90296,"mean_force":0.84087,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5278,0.06393,0.09369]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5024,0.07434,0.04406],"force_p95":79.88395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.50962,"mean_force":21.57575,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49908,0.08603,0.0412]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.5263,0.02421,0.02755],"force_p95":1.97108,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26857,"mean_force":0.76319,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5031,0.07409,0.04379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5038,0.05865,0.00963],"force_p95":2.0433,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36442,"mean_force":1.02281,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49643,0.09898,0.04665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.50311,0.06744,0.00933],"force_p95":0.56216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56483,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49908,0.15658,0.17585]},{"body_a":"attachment","body_b":"peg","contact_count":416.0,"contact_point_centroid":[0.50127,0.08105,0.0505],"force_p95":1.8276,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.02981,"mean_force":1.32549,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49667,0.09286,0.04393]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47464,-0.0293,0.05849],"force_p95":1.06919,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21423,"mean_force":0.43401,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50725,0.06017,0.0725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.50582,-0.04626,0.0081],"force_p95":0.69689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91985,"mean_force":0.60401,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52071,0.00904,0.11117]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.07104,0.0242],"force_p95":0.35117,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35117,"mean_force":0.35117,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.52962,0.04615,0.10059]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50444,-0.04622,0.02417],"final_tcp_position":[0.50306,-0.06213,0.13167],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1109.58698,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5465,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.4994,0.11477,0.05778],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50354,0.0598,0.03616],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.1399,"object_to_goal_dist_start":0.14759,"object_z_max":0.03616,"peak_contact_force":2.36442,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1416.0,"raw_peak_contact_force":2.36442,"tcp_end":[0.49692,0.08868,0.04218],"tcp_start":[0.4994,0.11477,0.05778],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":712.0,"n_steps_budget":900.0,"object_pos_end":[0.50657,-0.04622,0.02414],"object_pos_start":[0.50354,0.0598,0.03616],"object_to_goal_dist_end":0.03789,"object_to_goal_dist_start":0.1399,"object_z_max":0.04082,"peak_contact_force":285.82797,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1416.0,"raw_peak_contact_force":1109.58698,"tcp_end":[0.53651,0.06657,0.09661],"tcp_start":[0.49692,0.08868,0.04218],"tcp_to_object_dist_end":0.13737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":990.0,"object_pos_end":[0.50444,-0.04622,0.02417],"object_pos_start":[0.50657,-0.04622,0.02414],"object_to_goal_dist_end":0.03757,"object_to_goal_dist_start":0.03789,"object_z_max":0.02443,"peak_contact_force":0.60592,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":410.0,"raw_peak_contact_force":158.71588,"tcp_end":[0.50306,-0.06213,0.13167],"tcp_start":[0.53651,0.06657,0.09661],"tcp_to_object_dist_end":0.10868,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```