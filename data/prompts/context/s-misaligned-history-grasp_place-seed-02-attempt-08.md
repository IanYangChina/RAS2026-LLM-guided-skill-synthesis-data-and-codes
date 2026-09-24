## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2318 | 0.57 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | time_limit | time_limit | time_limit | 20  | 0.1407 | 0.96 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1660 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1129 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1377 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.138) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    descend_grasp_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    descend_grasp_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    descend_grasp_z:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.07
    orientation:
      mode: keep_current
  parameters:
    approach_goal_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_goal_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_goal_z:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.07
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_grasp_x: status=consumed; consumers=target.offset.x (add)
    - descend_grasp_y: status=consumed; consumers=target.offset.y (add)
    - descend_grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.07]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_x: status=consumed; consumers=target.offset.x (add)
    - approach_goal_y: status=consumed; consumers=target.offset.y (add)
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (add)
    - place_y: status=consumed; consumers=target.offset.y (add)
    - place_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.138
- **task_score** (E): 0.953
- **fitness_score**: 0.958  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2014 |
| descend_to_grasp | 1.00 | 1.00 | 0.0898 |
| grasp | 1.00 | 1.00 | 0.0121 |
| lift | 0.33 | 1.00 | 0.1621 |
| approach_goal | 0.33 | 1.00 | 0.1607 |
| descend_to_place | 1.00 | 1.00 | 0.1019 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.524, -0.020, 0.107) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.524, -0.020, 0.107)→(0.504, -0.017, 0.023) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.504, -0.017, 0.023)→(0.496, -0.017, 0.014) | (0.493, -0.015, 0.026)→(0.492, -0.017, 0.025) | 0.281→0.283 | 1.00 / 44.667 | 0.179 | 0.294 |
| lift | lift | 0.33 / step_budget | (0.496, -0.017, 0.014)→(0.489, -0.017, 0.176) | (0.492, -0.017, 0.025)→(0.500, -0.017, 0.181) | 0.283→0.239 | 1.00 / 39.333 | 0.076 | 1.060 |
| approach_goal | approach | 0.33 / step_budget | (0.489, -0.017, 0.176)→(0.590, 0.099, 0.211) | (0.500, -0.017, 0.181)→(0.596, 0.099, 0.203) | 0.239→0.101 | 1.00 / 39.333 | 0.078 | 0.104 |
| descend_to_place | descend | 1.00 / step_budget | (0.590, 0.099, 0.211)→(0.623, 0.175, 0.166) | (0.596, 0.099, 0.203)→(0.627, 0.175, 0.154) | 0.101→0.018 | 1.00 / 38.667 | 0.080 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.170
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.769
- phase_breakdown.lift_object_score: 0.871
- phase_breakdown.reach_object_score: 0.113
- phase_breakdown.place_goal_score: 0.970
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.158
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02158,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.01404,"approach_goal.approach_goal_y":-0.02997,"approach_goal.approach_goal_z":0.06977,"approach_goal.approach_speed":0.19505,"approach_object.approach_offset_x":0.01309,"approach_object.approach_offset_y":-0.00109,"approach_object.approach_offset_z":0.08338,"descend_to_grasp.descend_grasp_x":0.01311,"descend_to_grasp.descend_grasp_y":-0.00096,"descend_to_grasp.descend_grasp_z":-0.0053,"descend_to_place.place_x":0.00604,"descend_to_place.place_y":0.00362,"descend_to_place.place_z":0.00962,"lift.lift_height":0.18982},"optimized_scores":{"best_composite_score":0.16118,"best_fitness_score":0.98118,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.47312,-0.02069,-0.0014],"force_p95":0.81057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05259,"mean_force":0.12677,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47467,-0.02069,0.01549]},{"body_a":"grasp_target","body_b":"hand","contact_count":626.0,"contact_point_centroid":[0.48984,-0.02299,0.10114],"force_p95":0.12708,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41755,"mean_force":0.06303,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47195,-0.02062,0.06268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19772.0,"contact_point_centroid":[0.47205,-0.00148,0.09432],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26649,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47184,-0.02062,0.09232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20109.0,"contact_point_centroid":[0.47204,-0.03975,0.09541],"force_p95":0.07101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26577,"mean_force":0.04967,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47184,-0.02062,0.09355]},{"body_a":"grasp_target","body_b":"hand","contact_count":401.0,"contact_point_centroid":[0.49401,-0.01986,0.0534],"force_p95":0.14372,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2258,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47694,-0.02074,0.01377]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47562,-0.02041,-0.00243],"force_p95":0.17505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21152,"mean_force":0.15287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47755,-0.02075,0.01437]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13772.0,"contact_point_centroid":[0.60624,0.10958,0.20525],"force_p95":0.09644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14074,"mean_force":0.06485,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60613,0.12876,0.20471]},{"body_a":"world","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49226,-0.00954,0.21139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18752.0,"contact_point_centroid":[0.60689,0.14753,0.20553],"force_p95":0.07515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13332,"mean_force":0.04807,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60611,0.12876,0.20469]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48369,-0.02019,0.06809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17274.0,"contact_point_centroid":[0.52271,0.01613,0.20291],"force_p95":0.08026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10792,"mean_force":0.0578,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52312,0.03534,0.20094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21027.0,"contact_point_centroid":[0.52274,0.05373,0.20222],"force_p95":0.0722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09972,"mean_force":0.04881,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52252,0.03475,0.20059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.47656,-0.00148,0.01513],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09567,"mean_force":0.04549,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47638,-0.02072,0.01321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4784.0,"contact_point_centroid":[0.47658,-0.03989,0.01508],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07488,"mean_force":0.04452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47637,-0.02072,0.01321]}],"total_contact_groups":14},"final_pose_error":0.01043,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63595,0.15992,0.17405],"final_tcp_position":[0.63202,0.15978,0.19127],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.05259,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48625,-0.01949,0.1227],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4843,-0.02091,0.02112],"tcp_start":[0.48625,-0.01949,0.1227],"tcp_to_object_dist_end":0.00953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47523,-0.02074,0.02487],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2899,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.16431,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11909.0,"raw_peak_contact_force":0.2258,"tcp_end":[0.47634,-0.02072,0.01318],"tcp_start":[0.4843,-0.02091,0.02112],"tcp_to_object_dist_end":0.01174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48532,-0.02047,0.18006],"object_pos_start":[0.47523,-0.02074,0.02487],"object_to_goal_dist_end":0.23178,"object_to_goal_dist_start":0.2899,"object_z_max":0.17987,"peak_contact_force":0.08276,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40667.0,"raw_peak_contact_force":1.05259,"subtask_id":"lift_object","tcp_end":[0.47167,-0.02062,0.1748],"tcp_start":[0.47634,-0.02072,0.01318],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58178,0.0872,0.21775],"object_pos_start":[0.48532,-0.02047,0.18006],"object_to_goal_dist_end":0.09174,"object_to_goal_dist_start":0.23178,"object_z_max":0.21772,"peak_contact_force":0.08186,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38301.0,"raw_peak_contact_force":0.10792,"subtask_id":"place_goal","tcp_end":[0.57377,0.08719,0.22898],"tcp_start":[0.47167,-0.02062,0.1748],"tcp_to_object_dist_end":0.01379,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.63595,0.15992,0.17405],"object_pos_start":[0.58178,0.0872,0.21775],"object_to_goal_dist_end":0.0166,"object_to_goal_dist_start":0.09174,"object_z_max":0.21775,"peak_contact_force":0.10149,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32524.0,"raw_peak_contact_force":0.14074,"subtask_id":"place_goal","tcp_end":[0.63202,0.15978,0.19127],"tcp_start":[0.57377,0.08719,0.22898],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03947,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.0089,"approach_goal.approach_goal_y":0.03661,"approach_goal.approach_goal_z":0.08134,"approach_goal.approach_speed":0.17505,"approach_object.approach_offset_x":0.04883,"approach_object.approach_offset_y":-0.02289,"approach_object.approach_offset_z":0.05412,"descend_to_grasp.descend_grasp_x":0.01583,"descend_to_grasp.descend_grasp_y":0.0051,"descend_to_grasp.descend_grasp_z":-0.00387,"descend_to_place.place_x":-0.00605,"descend_to_place.place_y":0.01763,"descend_to_place.place_z":0.00437,"lift.lift_height":0.21097},"optimized_scores":{"best_composite_score":0.09435,"best_fitness_score":0.91435,"best_task_score":0.86017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.45536,-0.02233,-0.0014],"force_p95":0.7478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96669,"mean_force":0.10488,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46377,-0.02376,0.02085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45904,-0.04278,0.10101],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33348,"mean_force":0.04941,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45881,-0.02362,0.09915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45901,-0.00448,0.10106],"force_p95":0.07339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.319,"mean_force":0.04865,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45881,-0.02362,0.09915]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45842,-0.02574,-0.00228],"force_p95":0.19448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29199,"mean_force":0.14439,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46667,-0.02384,0.01951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4659.0,"contact_point_centroid":[0.46571,-0.00463,0.02035],"force_p95":0.07843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14216,"mean_force":0.04527,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46553,-0.02381,0.0184]},{"body_a":"world","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50031,-0.0227,0.19519]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48722,-0.03547,0.05862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.57854,0.15205,0.14581],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11212,"mean_force":0.04836,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57824,0.17118,0.14385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.57849,0.19032,0.14565],"force_p95":0.0716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10935,"mean_force":0.04861,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57824,0.17118,0.14385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50094,0.03452,0.18192],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09907,"mean_force":0.04875,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50067,0.05367,0.18005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5124.0,"contact_point_centroid":[0.46576,-0.04323,0.02031],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09265,"mean_force":0.04517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46555,-0.02381,0.01841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50088,0.0728,0.18196],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08085,"mean_force":0.04851,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50067,0.05367,0.18005]}],"total_contact_groups":12},"final_pose_error":0.02563,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60803,0.20734,0.10948],"final_tcp_position":[0.60639,0.20737,0.12011],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.96669,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50278,-0.04588,0.09208],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47338,-0.02412,0.02608],"tcp_start":[0.50278,-0.04588,0.09208],"tcp_to_object_dist_end":0.01498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45839,-0.02368,0.02504],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30201,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.18092,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11583.0,"raw_peak_contact_force":0.29199,"tcp_end":[0.46551,-0.02381,0.01838],"tcp_start":[0.47338,-0.02412,0.02608],"tcp_to_object_dist_end":0.00975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46317,-0.02359,0.18241],"object_pos_start":[0.45839,-0.02368,0.02504],"object_to_goal_dist_end":0.29372,"object_to_goal_dist_start":0.30201,"object_z_max":0.18221,"peak_contact_force":0.07381,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40158.0,"raw_peak_contact_force":0.96669,"subtask_id":"lift_object","tcp_end":[0.45638,-0.02357,0.18132],"tcp_start":[0.46551,-0.02381,0.01838],"tcp_to_object_dist_end":0.00688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54491,0.12167,0.17566],"object_pos_start":[0.46317,-0.02359,0.18241],"object_to_goal_dist_end":0.13616,"object_to_goal_dist_start":0.29372,"object_z_max":0.18252,"peak_contact_force":0.07469,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.09907,"subtask_id":"place_goal","tcp_end":[0.54243,0.12163,0.18244],"tcp_start":[0.45638,-0.02357,0.18132],"tcp_to_object_dist_end":0.00722,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60803,0.20734,0.10948],"object_pos_start":[0.54491,0.12167,0.17566],"object_to_goal_dist_end":0.02259,"object_to_goal_dist_start":0.13616,"object_z_max":0.17566,"peak_contact_force":0.07051,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.11212,"subtask_id":"place_goal","tcp_end":[0.60639,0.20737,0.12011],"tcp_start":[0.54243,0.12163,0.18244],"tcp_to_object_dist_end":0.01076,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02113,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.03322,"approach_goal.approach_goal_y":-0.04949,"approach_goal.approach_goal_z":0.05405,"approach_goal.approach_speed":0.19006,"approach_object.approach_offset_x":0.04863,"approach_object.approach_offset_y":0.00503,"approach_object.approach_offset_z":0.07452,"descend_to_grasp.descend_grasp_x":0.01223,"descend_to_grasp.descend_grasp_y":-0.0082,"descend_to_grasp.descend_grasp_z":-0.00962,"descend_to_place.place_x":-0.0148,"descend_to_place.place_y":0.00629,"descend_to_place.place_z":0.00289,"lift.lift_height":0.20371},"optimized_scores":{"best_composite_score":0.15752,"best_fitness_score":0.97752,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.54104,-0.00577,-0.00168],"force_p95":0.8379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15951,"mean_force":0.15,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5433,-0.00575,0.01272]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.5556,-0.00538,0.12865],"force_p95":0.19194,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41333,"mean_force":0.10735,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54016,-0.00578,0.08933]},{"body_a":"grasp_target","body_b":"hand","contact_count":424.0,"contact_point_centroid":[0.56233,0.00694,0.05186],"force_p95":0.34441,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36391,"mean_force":0.21205,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54643,-0.00569,0.01125]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54355,-0.00208,-0.00274],"force_p95":0.32184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35647,"mean_force":0.19709,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54681,-0.00569,0.01171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54038,0.01336,0.09121],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26434,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54016,-0.00578,0.08933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54041,-0.02491,0.09122],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25811,"mean_force":0.0498,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54016,-0.00578,0.08933]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.54098,0.00287,0.20146]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.56813,0.00032,0.06373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9460.0,"contact_point_centroid":[0.63941,0.14387,0.20283],"force_p95":0.06737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11523,"mean_force":0.04513,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63966,0.12471,0.20055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20425.0,"contact_point_centroid":[0.59699,0.06202,0.19777],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10522,"mean_force":0.04879,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59687,0.04291,0.19574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8964.0,"contact_point_centroid":[0.63884,0.10681,0.20226],"force_p95":0.06951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1041,"mean_force":0.04707,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63927,0.12602,0.19993]},{"body_a":"grasp_target","body_b":"hand","contact_count":183.0,"contact_point_centroid":[0.54696,0.01899,0.2139],"force_p95":0.06073,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10377,"mean_force":0.03617,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55015,0.00464,0.17362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19450.0,"contact_point_centroid":[0.59468,0.02209,0.19672],"force_p95":0.0733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10305,"mean_force":0.05097,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5948,0.04124,0.19472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5604.0,"contact_point_centroid":[0.54573,0.01503,0.01212],"force_p95":0.07821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09958,"mean_force":0.05238,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54554,-0.00567,0.01023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3707.0,"contact_point_centroid":[0.54569,-0.02472,0.01207],"force_p95":0.07054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08853,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54549,-0.00568,0.01017]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63702,0.15757,0.17888],"final_tcp_position":[0.63057,0.15754,0.18707],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.15951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.58352,0.00571,0.10768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55453,-0.00561,0.0207],"tcp_start":[0.58352,0.00571,0.10768],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54329,-0.00577,0.02412],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25616,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.19238,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11535.0,"raw_peak_contact_force":0.36391,"tcp_end":[0.54547,-0.00573,0.01015],"tcp_start":[0.55453,-0.00561,0.0207],"tcp_to_object_dist_end":0.01413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55068,-0.00576,0.1802],"object_pos_start":[0.54329,-0.00577,0.02412],"object_to_goal_dist_end":0.19068,"object_to_goal_dist_start":0.25616,"object_z_max":0.18002,"peak_contact_force":0.07148,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41200.0,"raw_peak_contact_force":1.15951,"subtask_id":"lift_object","tcp_end":[0.53978,-0.00578,0.1715],"tcp_start":[0.54547,-0.00573,0.01015],"tcp_to_object_dist_end":0.01395,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.66014,0.08768,0.21701],"object_pos_start":[0.55068,-0.00576,0.1802],"object_to_goal_dist_end":0.07606,"object_to_goal_dist_start":0.19068,"object_z_max":0.21698,"peak_contact_force":0.07862,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40058.0,"raw_peak_contact_force":0.10522,"subtask_id":"place_goal","tcp_end":[0.65255,0.08775,0.22291],"tcp_start":[0.53978,-0.00578,0.1715],"tcp_to_object_dist_end":0.00961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.63702,0.15757,0.17888],"object_pos_start":[0.66014,0.08768,0.21701],"object_to_goal_dist_end":0.01619,"object_to_goal_dist_start":0.07606,"object_z_max":0.21701,"peak_contact_force":0.06884,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18424.0,"raw_peak_contact_force":0.11523,"subtask_id":"place_goal","tcp_end":[0.63057,0.15754,0.18707],"tcp_start":[0.65255,0.08775,0.22291],"tcp_to_object_dist_end":0.01043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```