## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1478 | 0.01 | ❌ rejected |
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1475 | 0.01 | ✅ accepted |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 2 | -0.0315 | 0.00 | ❌ rejected |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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

## Current Skill (Q=-0.148) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 5.0
      - 40.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
      - path: guards.guard_force_below.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: guard_force_below
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04]
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=termination.force_threshold (replace), guards.guard_force_below.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=guard_force_below, when=during_phase, predicate=force_below, on_failure=retry, threshold=20.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.148
- **task_score** (E): 0.007
- **fitness_score**: 0.162  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2542 |
| contact_peg | 1.00 | 1.00 | 0.0103 |
| push_along_channel | 0.00 | 1.00 | 0.0000 |
| retract | 0.33 | 1.00 | 0.1033 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.127, 0.059) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.667 | 212.122 | 251.304 |
| contact_peg | align | 1.00 / step_budget | (0.513, 0.127, 0.059)→(0.515, 0.119, 0.054) | (0.503, 0.080, 0.034)→(0.503, 0.078, 0.034) | 0.160→0.158 | 1.00 / 1.667 | 222.780 | 223.279 |
| push_along_channel | push | 0.00 / guard_failure | (0.515, 0.119, 0.054)→(0.515, 0.119, 0.054) | (0.503, 0.078, 0.034)→(0.503, 0.078, 0.034) | 0.158→0.158 | 1.00 / 2.000 | 70.223 | 73.359 |
| retract | retract | 0.33 / step_budget | (0.515, 0.119, 0.054)→(0.512, 0.118, 0.158) | (0.504, 0.078, 0.034)→(0.504, 0.078, 0.034) | 0.158→0.158 | 1.00 / 1.000 | 0.543 | 75.768 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.034
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.022
- phase_score: 0.339
- phase_breakdown.push_score: 0.011
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.841

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.212
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.022
- **Median Q (composite search score)**: -0.173
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.359


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56522,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.0723,"contact_peg.contact_speed":0.02757,"push_along_channel.push_force_limit":6.49307,"push_along_channel.push_speed":0.00678,"retract.retract_speed":0.07136},"optimized_scores":{"best_composite_score":-0.09764,"best_fitness_score":0.21236,"best_task_score":0.02239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54062,0.11999,0.05987],"force_p95":158.46447,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":162.09664,"mean_force":119.82642,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.4881,0.14557,0.03485]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54099,0.11999,0.05985],"force_p95":66.7811,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.17612,"mean_force":49.87657,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4886,0.1453,0.03477]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54087,0.11999,0.05979],"force_p95":60.48002,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.10872,"mean_force":55.87655,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48844,0.14537,0.03466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":99.0,"contact_point_centroid":[0.49571,0.11554,0.00947],"force_p95":13.89867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.13794,"mean_force":1.86447,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.48454,0.1532,0.04168]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.49488,0.13509,0.04953],"force_p95":15.69348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.8501,"mean_force":7.46608,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.48729,0.14677,0.03588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":761.0,"contact_point_centroid":[0.49624,0.11906,0.00942],"force_p95":0.61263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5513,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49061,0.17924,0.17069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49954,0.11336,0.00942],"force_p95":0.61079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28876,"mean_force":0.54537,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4852,0.14439,0.09288]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49949,0.19931,0.29774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.48164,0.12,0.00983],"force_p95":0.71343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71594,"mean_force":0.69083,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48847,0.14537,0.03466]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49767,0.13314,0.05834],"force_p95":0.23488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25096,"mean_force":0.1317,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48683,0.14473,0.0388]}],"total_contact_groups":10},"final_pose_error":0.03379,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49944,0.11356,0.03392],"final_tcp_position":[0.48542,0.14445,0.15102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":162.09664,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.119,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48516,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":785.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48316,0.16006,0.04935],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":690.0,"object_pos_end":[0.49814,0.11505,0.03532],"object_pos_start":[0.496,0.119,0.03392],"object_to_goal_dist_end":0.19511,"object_to_goal_dist_start":0.19914,"object_z_max":0.03587,"peak_contact_force":162.09664,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":125.0,"raw_peak_contact_force":162.09664,"subtask_id":"contact","tcp_end":[0.48839,0.14539,0.03467],"tcp_start":[0.48316,0.16006,0.04935],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49829,0.11485,0.03509],"object_pos_start":[0.49814,0.11505,0.03532],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.19511,"object_z_max":0.03532,"peak_contact_force":51.6992,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":61.10872,"subtask_id":"push","tcp_end":[0.48854,0.14534,0.03466],"tcp_start":[0.48849,0.14536,0.03466],"tcp_to_object_dist_end":0.03202,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49944,0.11356,0.03392],"object_pos_start":[0.49861,0.11447,0.03467],"object_to_goal_dist_end":0.19366,"object_to_goal_dist_start":0.19455,"object_z_max":0.03467,"peak_contact_force":0.53071,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1009.0,"raw_peak_contact_force":68.17612,"tcp_end":[0.48542,0.14445,0.15102],"tcp_start":[0.48854,0.14534,0.03466],"tcp_to_object_dist_end":0.12192,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1844,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09973,"contact_peg.contact_speed":0.023,"push_along_channel.push_force_limit":20.52863,"push_along_channel.push_speed":0.04398,"retract.retract_speed":0.06014},"optimized_scores":{"best_composite_score":-0.17291,"best_fitness_score":0.13709,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":115.0,"contact_point_centroid":[0.53492,0.11261,0.05978],"force_p95":347.0184,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.91159,"mean_force":318.01151,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52378,0.11269,0.06401]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":999.0,"contact_point_centroid":[0.53646,0.11101,0.05994],"force_p95":252.69301,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.01286,"mean_force":229.01478,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.5254,0.11108,0.06453]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53659,0.10796,0.05996],"force_p95":76.53297,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.69514,"mean_force":57.45043,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52552,0.10806,0.06454]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53659,0.10798,0.05995],"force_p95":79.62423,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.6429,"mean_force":79.30019,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52552,0.10809,0.06453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":880.0,"contact_point_centroid":[0.50586,0.063,0.00937],"force_p95":0.55583,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56193,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51236,0.14947,0.16227]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49981,0.19844,0.29608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50598,0.063,0.00938],"force_p95":0.55193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54651,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.5254,0.11108,0.06453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50597,0.06296,0.00939],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54629,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52215,0.10737,0.11388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5086,0.04634,0.00939],"force_p95":0.54733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54752,"mean_force":0.54598,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52552,0.10809,0.06453]}],"total_contact_groups":9},"final_pose_error":0.0507,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.06297,0.03386],"final_tcp_position":[0.52235,0.1074,0.16393],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":359.91159,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":908.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":317.58651,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1029.0,"raw_peak_contact_force":359.91159,"subtask_id":"approach","tcp_end":[0.52449,0.11266,0.06453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06291,0.03385],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14316,"object_to_goal_dist_start":0.1432,"object_z_max":0.03385,"peak_contact_force":253.18189,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1998.0,"raw_peak_contact_force":254.01286,"subtask_id":"contact","tcp_end":[0.52552,0.10809,0.06453],"tcp_start":[0.52449,0.11266,0.06453],"tcp_to_object_dist_end":0.05799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06289,0.03385],"object_pos_start":[0.50603,0.06291,0.03385],"object_to_goal_dist_end":0.14315,"object_to_goal_dist_start":0.14316,"object_z_max":0.03385,"peak_contact_force":79.6429,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":79.6429,"subtask_id":"push","tcp_end":[0.52552,0.10807,0.06453],"tcp_start":[0.52552,0.10808,0.06453],"tcp_to_object_dist_end":0.05801,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.06297,0.03386],"object_pos_start":[0.50592,0.06291,0.03384],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.55291,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":79.69514,"tcp_end":[0.52235,0.1074,0.16393],"tcp_start":[0.52552,0.10807,0.06453],"tcp_to_object_dist_end":0.13844,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83333,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04829,"contact_peg.contact_speed":0.02464,"push_along_channel.push_force_limit":23.14923,"push_along_channel.push_speed":0.01691,"retract.retract_speed":0.05682},"optimized_scores":{"best_composite_score":-0.17291,"best_fitness_score":0.13709,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":119.0,"contact_point_centroid":[0.54093,0.1069,0.05981],"force_p95":340.35627,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.75166,"mean_force":316.46383,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52973,0.10708,0.06392]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":999.0,"contact_point_centroid":[0.54151,0.1051,0.05995],"force_p95":251.41455,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.72656,"mean_force":212.72453,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.53035,0.10528,0.0643]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.54115,0.10188,0.05996],"force_p95":76.20253,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.43148,"mean_force":56.71595,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52995,0.10212,0.06421]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54115,0.10191,0.05995],"force_p95":79.2983,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.32616,"mean_force":78.84806,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52995,0.10214,0.0642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50599,0.05663,0.00936],"force_p95":0.6019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56297,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51565,0.14663,0.16317]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49979,0.19846,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50614,0.05658,0.00938],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55133,"mean_force":0.54674,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"align","tcp_position_centroid":[0.53035,0.10528,0.0643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50599,0.06852,0.00938],"force_p95":0.54963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54672,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52995,0.10214,0.0642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05658,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52654,0.10146,0.11099]}],"total_contact_groups":9},"final_pose_error":0.05603,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.05663,0.03378],"final_tcp_position":[0.52675,0.1015,0.15827],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":391.75166,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":318.29582,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1127.0,"raw_peak_contact_force":391.75166,"subtask_id":"approach","tcp_end":[0.53043,0.10707,0.0643],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13689,"object_z_max":0.03378,"peak_contact_force":253.06185,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1998.0,"raw_peak_contact_force":253.72656,"subtask_id":"contact","tcp_end":[0.52994,0.10215,0.0642],"tcp_start":[0.53043,0.10707,0.0643],"tcp_to_object_dist_end":0.05972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":79.32616,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":79.32616,"subtask_id":"push","tcp_end":[0.52995,0.10213,0.0642],"tcp_start":[0.52995,0.10213,0.0642],"tcp_to_object_dist_end":0.05969,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50615,0.0566,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.545,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":79.43148,"tcp_end":[0.52675,0.1015,0.15827],"tcp_start":[0.52995,0.10213,0.0642],"tcp_to_object_dist_end":0.13392,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```